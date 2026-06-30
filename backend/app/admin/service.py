from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.listings.models import Listing, ListingStatus


async def get_stats(db: AsyncSession) -> dict:
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )
    total_listings = await db.scalar(select(func.count(Listing.id)))
    active_listings = await db.scalar(
        select(func.count(Listing.id)).where(Listing.status == ListingStatus.active)
    )
    sold_listings = await db.scalar(
        select(func.count(Listing.id)).where(Listing.status == ListingStatus.sold)
    )

    return {
        "total_users": total_users or 0,
        "active_users": active_users or 0,
        "total_listings": total_listings or 0,
        "active_listings": active_listings or 0,
        "sold_listings": sold_listings or 0,
    }


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[User]:
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def set_user_active_status(db: AsyncSession, user_id: int, is_active: bool) -> User | None:
    user = await db.get(User, user_id)
    if not user:
        return None
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    return user


async def get_all_listings(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Listing]:
    result = await db.execute(
        select(Listing).order_by(Listing.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def delete_listing(db: AsyncSession, listing_id: int) -> bool:
    listing = await db.get(Listing, listing_id)
    if not listing:
        return False
    await db.delete(listing)
    await db.commit()
    return True