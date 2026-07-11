import os
import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.cache import get_cached, set_cached, invalidate_pattern
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

UPLOAD_DIR = f"{settings.UPLOAD_DIR}/listings"
os.makedirs(UPLOAD_DIR, exist_ok=True)


LISTINGS_CACHE_TTL = 30


def build_listings_cache_key(
    category: str | None,
    min_price: float | None,
    max_price: float | None,
) -> str:
    
    return f"listings:all:category={category}:min_price={min_price}:max_price={max_price}"


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
    cache_key = build_listings_cache_key(category, min_price, max_price)

    
    cached_result = await get_cached(cache_key)
    if cached_result is not None:
        return cached_result

    listings = await get_all_listings(db, category, min_price, max_price)
    result = [ListingShortResponse.model_validate(l) for l in listings]

    
    serializable_result = [item.model_dump(mode="json") for item in result]
    await set_cached(cache_key, serializable_result, LISTINGS_CACHE_TTL)

    return result


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
    "/upload-image",
    status_code=status.HTTP_201_CREATED,
)
async def upload_listing_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дозволені тільки jpeg, png, webp",
        )

    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"url": f"/uploads/listings/{filename}"}


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

  
    await invalidate_pattern("listings:all:*")

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

    await invalidate_pattern("listings:all:*")

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

    await invalidate_pattern("listings:all:*")