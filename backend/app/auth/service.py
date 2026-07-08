import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password, verify_password, create_access_token
from app.core.redis import get_redis
from app.auth.models import User
from app.auth.schemas import UserRegister, UserUpdate, TokenResponse

# Скільки секунд посилання для скидання пароля лишається дійсним.
# Довше за OAuth-state (5 хв), бо тут юзеру треба встигнути відкрити
# поштову скриньку - на відміну від OAuth, де редірект миттєвий.
PASSWORD_RESET_TTL_SECONDS = 900  # 15 хвилин


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def register_user(data: UserRegister, db: AsyncSession) -> User:
    existing_user = await get_user_by_email(data.email, db)
    if existing_user:
        raise ValueError("Користувач з таким email вже існує")

    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )

    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    return new_user


async def login_user(email: str, password: str, db: AsyncSession) -> TokenResponse:
    user = await get_user_by_email(email, db)

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Невірний email або пароль")

    if not user.is_active:
        raise ValueError("Акаунт заблокований")

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token)


async def update_user(user: User, data: UserUpdate, db: AsyncSession) -> User:
    update_data = data.model_dump(exclude_none=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def create_password_reset_token(email: str, db: AsyncSession) -> tuple[User, str] | None:
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        return None

    token = secrets.token_urlsafe(32)

    redis = await get_redis()
    if redis is not None:
        await redis.set(
            f"password_reset:{token}",
            str(user.id),
            ex=PASSWORD_RESET_TTL_SECONDS,
        )

    return user, token


async def reset_password_with_token(token: str, new_password: str, db: AsyncSession) -> None:
   
    redis = await get_redis()
    if redis is None:
        raise ValueError("Сервіс тимчасово недоступний, спробуйте пізніше")

    redis_key = f"password_reset:{token}"
    user_id_raw = await redis.get(redis_key)

    if user_id_raw is None:
        raise ValueError("Посилання для скидання пароля недійсне або застаріло")

   
    await redis.delete(redis_key)

    user = await get_user_by_id(int(user_id_raw), db)
    if user is None:
        raise ValueError("Користувача не знайдено")

    user.hashed_password = hash_password(new_password)
    await db.flush()
    await db.refresh(user)