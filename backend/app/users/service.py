from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.models import User
from app.auth.service import get_user_by_id
from app.users.schemas import UserPublicResponse


async def get_user_public(user_id: int, db: AsyncSession) -> UserPublicResponse | None:
    user = await get_user_by_id(user_id, db)
    if user is None:
        return None
    return UserPublicResponse.model_validate(user)


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).where(User.is_active == True))
    return list(result.scalars().all())


async def deactivate_user(user: User, db: AsyncSession) -> User:
    user.is_active = False
    await db.flush()
    await db.refresh(user)
    return user