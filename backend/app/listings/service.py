from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.models import User
from app.listings.models import Listing, ListingStatus
from app.listings.schemas import ListingCreate, ListingUpdate


async def get_listing_by_id(listing_id: int, db: AsyncSession) -> Listing | None:
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    return result.scalar_one_or_none()


async def get_all_listings(
    db: AsyncSession,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[Listing]:
    query = select(Listing).where(Listing.status == ListingStatus.active)

    if category:
        query = query.where(Listing.category == category)
    if min_price is not None:
        query = query.where(Listing.price >= min_price)
    if max_price is not None:
        query = query.where(Listing.price <= max_price)

    query = query.order_by(Listing.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_seller_listings(seller_id: int, db: AsyncSession) -> list[Listing]:
    result = await db.execute(
        select(Listing)
        .where(Listing.seller_id == seller_id)
        .order_by(Listing.created_at.desc())
    )
    return list(result.scalars().all())


async def create_listing(
    data: ListingCreate,
    seller: User,
    db: AsyncSession,
) -> Listing:
    listing = Listing(
        title=data.title,
        description=data.description,
        price=data.price,
        condition=data.condition,
        category=data.category,
        image_urls=data.image_urls,
        seller_id=seller.id,
    )

    db.add(listing)
    await db.flush()
    await db.refresh(listing)
    return listing


async def update_listing(
    listing: Listing,
    data: ListingUpdate,
    db: AsyncSession,
) -> Listing:
    update_data = data.model_dump(exclude_none=True)

    for field, value in update_data.items():
        setattr(listing, field, value)

    await db.flush()
    await db.refresh(listing)
    return listing


async def delete_listing(listing: Listing, db: AsyncSession) -> None:
    await db.delete(listing)
    await db.flush()