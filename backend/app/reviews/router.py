from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.models import User
from app.auth.dependencies import get_current_active_user
from app.reviews.schemas import ReviewCreate, ReviewResponse, ReviewShortResponse, SellerRatingResponse
from app.reviews.service import (
    get_review_by_id,
    get_listing_reviews,
    get_seller_reviews,
    get_seller_rating,
    create_review,
    delete_review,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get(
    "/listings/{listing_id}",
    response_model=list[ReviewShortResponse],
)
async def list_listing_reviews(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[ReviewShortResponse]:
    reviews = await get_listing_reviews(listing_id, db)
    return [ReviewShortResponse.model_validate(r) for r in reviews]


@router.get(
    "/sellers/{seller_id}",
    response_model=list[ReviewShortResponse],
)
async def list_seller_reviews(
    seller_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[ReviewShortResponse]:
    reviews = await get_seller_reviews(seller_id, db)
    return [ReviewShortResponse.model_validate(r) for r in reviews]


@router.get(
    "/sellers/{seller_id}/rating",
    response_model=SellerRatingResponse,
)
async def get_rating(
    seller_id: int,
    db: AsyncSession = Depends(get_db),
) -> SellerRatingResponse:
    return await get_seller_rating(seller_id, db)


@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    try:
        review = await create_review(data, current_user, db)
        return ReviewResponse.model_validate(review)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    review = await get_review_by_id(review_id, db)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Відгук не знайдено",
        )
    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не можете видалити чужий відгук",
        )
    await delete_review(review, db)