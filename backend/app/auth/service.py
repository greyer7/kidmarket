from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password, verify_password, create_access_token
from app.auth.models import User
from app.auth.schemas import UserRegister, UserUpdate, TokenResponse


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