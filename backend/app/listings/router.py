from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.models import User
from app.auth.dependencies import get_current_active_user
from app.listings.models import Listing
from app.listings.schemas import (
    ListingCreate,
    ListingUpdate,
    ListingResponse,
    ListingShortResponse,
)
from app.listings.service import (
    get_listing_by_id,
    get_all_listings,
    get_seller_listings,
    create_listing,
    update_listing,
    delete_listing,
)

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get(
    "/",
    response_model=list[ListingShortResponse],
)
async def list_listings(
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[ListingShortResponse]:
    listings = await get_all_listings(db, category, min_price, max_price)
    return [ListingShortResponse.model_validate(l) for l in listings]


@router.get(
    "/my",
    response_model=list[ListingShortResponse],
)
async def list_my_listings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[ListingShortResponse]:
    listings = await get_seller_listings(current_user.id, db)
    return [ListingShortResponse.model_validate(l) for l in listings]


@router.post(
    "/",
    response_model=ListingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_listing(
    data: ListingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ListingResponse:
    listing = await create_listing(data, current_user, db)
    return ListingResponse.model_validate(listing)


@router.get(
    "/{listing_id}",
    response_model=ListingResponse,
)
async def get_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
) -> ListingResponse:
    listing = await get_listing_by_id(listing_id, db)
    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оголошення не знайдено",
        )
    return ListingResponse.model_validate(listing)


@router.patch(
    "/{listing_id}",
    response_model=ListingResponse,
)
async def update_existing_listing(
    listing_id: int,
    data: ListingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ListingResponse:
    listing = await get_listing_by_id(listing_id, db)
    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оголошення не знайдено",
        )
    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не можете редагувати чуже оголошення",
        )
    updated = await update_listing(listing, data, db)
    return ListingResponse.model_validate(updated)


@router.delete(
    "/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_listing(
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    listing = await get_listing_by_id(listing_id, db)
    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оголошення не знайдено",
        )
    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не можете видалити чуже оголошення",
        )
    await delete_listing(listing, db)