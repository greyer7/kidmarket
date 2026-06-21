from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.auth.models import User
from app.reviews.models import Review
from app.reviews.schemas import ReviewCreate, SellerRatingResponse
from app.listings.models import Listing


async def get_review_by_id(review_id: int, db: AsyncSession) -> Review | None:
    result = await db.execute(select(Review).where(Review.id == review_id))
    return result.scalar_one_or_none()


async def get_listing_reviews(listing_id: int, db: AsyncSession) -> list[Review]:
    result = await db.execute(
        select(Review)
        .where(Review.listing_id == listing_id)
        .order_by(Review.created_at.desc())
    )
    return list(result.scalars().all())


async def get_seller_reviews(seller_id: int, db: AsyncSession) -> list[Review]:
    result = await db.execute(
        select(Review)
        .where(Review.seller_id == seller_id)
        .order_by(Review.created_at.desc())
    )
    return list(result.scalars().all())


async def get_seller_rating(seller_id: int, db: AsyncSession) -> SellerRatingResponse:
    result = await db.execute(
        select(
            func.avg(Review.rating),
            func.count(Review.id),
        ).where(Review.seller_id == seller_id)
    )
    row = result.one()
    average = round(float(row[0] or 0), 1)
    total = row[1]

    return SellerRatingResponse(
        seller_id=seller_id,
        average_rating=average,
        total_reviews=total,
    )


async def create_review(
    data: ReviewCreate,
    reviewer: User,
    db: AsyncSession,
) -> Review:
    listing_result = await db.execute(
        select(Listing).where(Listing.id == data.listing_id)
    )
    listing = listing_result.scalar_one_or_none()

    if listing is None:
        raise ValueError("Оголошення не знайдено")

    if listing.seller_id == reviewer.id:
        raise ValueError("Не можна залишати відгук на власне оголошення")

    existing = await db.execute(
        select(Review).where(
            Review.reviewer_id == reviewer.id,
            Review.listing_id == data.listing_id,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Ви вже залишили відгук на це оголошення")

    review = Review(
        rating=data.rating,
        comment=data.comment,
        reviewer_id=reviewer.id,
        seller_id=listing.seller_id,
        listing_id=data.listing_id,
    )

    db.add(review)
    await db.flush()
    await db.refresh(review)
    return review


async def delete_review(review: Review, db: AsyncSession) -> None:
    await db.delete(review)
    await db.flush()