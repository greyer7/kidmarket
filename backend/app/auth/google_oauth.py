"""
OAuth 2.0 авторизація через Google.

Flow:
1. GET  /api/auth/google           -> генеруємо state (CSRF-захист), зберігаємо в Redis,
                                       редіректимо користувача на Google.
2. Google -> користувач логіниться на стороні Google.
3. GET  /api/auth/google/callback  -> Google повертає ?code=...&state=...
                                       - звіряємо state з Redis
                                       - обмінюємо code на access_token Google
                                       - отримуємо email/ім'я/аватар користувача з Google
                                       - шукаємо або створюємо User в нашій БД
                                       - видаємо ВЛАСНИЙ JWT (як при звичайному логіні)
"""
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import create_access_token
from app.auth.models import User
from app.auth.schemas import TokenResponse
from app.auth.service import get_user_by_email

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# Скільки часу "state" вважається дійсним (захист від CSRF та застарілих запитів)
STATE_TTL_SECONDS = 300  # 5 хвилин

router = APIRouter(prefix="/google", tags=["auth"])


@router.get("")
async def google_login():
    """
    Крок 1: генеруємо унікальний state, кладемо його в Redis
    і повертаємо URL для редіректу на Google.
    """
    state = secrets.token_urlsafe(32)

    redis = await get_redis()
    await redis.set(f"oauth:google:state:{state}", "1", ex=STATE_TTL_SECONDS)

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    authorize_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    return {"authorize_url": authorize_url}


@router.get("/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """
    Крок 2: Google редіректить сюди з code + state.
    Перевіряємо state, обмінюємо code на токен Google, тягнемо профіль,
    знаходимо/створюємо користувача, видаємо власний JWT.
    """
    redis = await get_redis()
    state_key = f"oauth:google:state:{state}"

    state_exists = await redis.get(state_key)
    if not state_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недійсний або застарілий state (можлива CSRF-атака)",
        )
    # State одноразовий - одразу видаляємо
    await redis.delete(state_key)

    # Обмінюємо authorization code на access_token Google
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не вдалося отримати токен від Google",
            )

        google_tokens = token_response.json()
        google_access_token = google_tokens.get("access_token")

        # Отримуємо профіль користувача з Google
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не вдалося отримати дані користувача від Google",
            )

        google_user = userinfo_response.json()

    google_id: str | None = google_user.get("sub")
    email: str | None = google_user.get("email")
    full_name: str | None = google_user.get("name") or email
    avatar_url: str | None = google_user.get("picture")
    email_verified: bool = google_user.get("email_verified", False)

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google не повернув необхідні дані користувача",
        )

    user = await get_or_create_google_user(
        google_id=google_id,
        email=email,
        full_name=full_name,
        avatar_url=avatar_url,
        email_verified=email_verified,
        db=db,
    )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Акаунт заблокований",
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    # Передаємо токен через fragment (#), а не query (?) -
    # fragment НІКОЛИ не потрапляє на сервер (ні в логи nginx, ні в мережевий трафік
    # після початкового запиту), обробляється лише JavaScript у браузері.
    redirect_url = f"{settings.FRONTEND_URL}/auth/callback#token={access_token}"
    return RedirectResponse(url=redirect_url)


async def get_or_create_google_user(
    google_id: str,
    email: str,
    full_name: str,
    avatar_url: str | None,
    email_verified: bool,
    db: AsyncSession,
) -> User:
    """
    Шукає користувача за google_id, потім за email (щоб не плодити дублів,
    якщо людина раніше реєструвалась звичайним способом з тим самим email).
    Якщо не знайдено - створює нового.
    """
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()
    if user:
        return user

    # Користувач міг раніше зареєструватись через email/пароль
    existing_user = await get_user_by_email(email, db)
    if existing_user:
        existing_user.google_id = google_id
        if not existing_user.avatar_url and avatar_url:
            existing_user.avatar_url = avatar_url
        await db.flush()
        await db.refresh(existing_user)
        return existing_user

    new_user = User(
        email=email,
        hashed_password=None,
        full_name=full_name,
        avatar_url=avatar_url,
        is_verified=email_verified,
        auth_provider="google",
        google_id=google_id,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    return new_user