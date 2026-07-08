from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.email import send_password_reset_email, send_verification_email
from app.auth.schemas import (
    UserRegister,
    UserResponse,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
)
from app.auth.service import (
    register_user,
    login_user,
    create_password_reset_token,
    reset_password_with_token,
    create_email_verification_token,
    verify_email_with_token,
    create_resend_verification_token,
)
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.auth.google_oauth import router as google_router

router = APIRouter(prefix="/auth", tags=["auth"])

# Підключаємо ендпоінти Google OAuth (/auth/google, /auth/google/callback)
router.include_router(google_router)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    try:
        user = await register_user(data, db)

        token = await create_email_verification_token(user)
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        background_tasks.add_task(
            send_verification_email,
            user.email,
            user.full_name,
            verify_link,
        )

        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        token = await login_user(form_data.username, form_data.password, db)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    ВАЖЛИВО: відповідь ЗАВЖДИ однакова, незалежно від того, чи існує такий
    email у базі. Це навмисний захист від "user enumeration" - зловмисник
    не повинен мати змогу дізнатись, які email зареєстровані в системі,
    просто пробуючи різні адреси і порівнюючи відповіді.
    """
    result = await create_password_reset_token(data.email, db)

    if result is not None:
        user, token = result
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            user.full_name,
            reset_link,
        )

    return {
        "message": "Якщо такий email зареєстрований, на нього надіслано лист із інструкціями"
    }


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        await reset_password_with_token(data.token, data.new_password, db)
        return {"message": "Пароль успішно змінено"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
)
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        await verify_email_with_token(data.token, db)
        return {"message": "Email успішно підтверджено"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/resend-verification",
    status_code=status.HTTP_200_OK,
)
async def resend_verification(
    data: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Та сама логіка "завжди однакова відповідь", що й у forgot_password.
    result = await create_resend_verification_token(data.email, db)

    if result is not None:
        user, token = result
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        background_tasks.add_task(
            send_verification_email,
            user.email,
            user.full_name,
            verify_link,
        )

    return {
        "message": "Якщо такий email зареєстрований і ще не підтверджений, на нього надіслано лист"
    }