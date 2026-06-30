from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.auth.models import User
from app.core.database import get_db
from app.admin import service
from app.admin.schemas import AdminUserResponse, AdminListingResponse, StatsResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await service.get_stats(db)


@router.get("/users", response_model=list[AdminUserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await service.get_all_users(db, skip, limit)


@router.patch("/users/{user_id}/active", response_model=AdminUserResponse)
async def set_user_active(
    user_id: int,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = await service.set_user_active_status(db, user_id, is_active)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Юзера не знайдено")
    return user


@router.get("/listings", response_model=list[AdminListingResponse])
async def get_listings(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await service.get_all_listings(db, skip, limit)


@router.delete("/listings/{listing_id}")
async def delete_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    deleted = await service.delete_listing(db, listing_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Оголошення не знайдено")
    return {"detail": "Оголошення видалено"}