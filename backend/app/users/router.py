import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.models import User
from app.auth.schemas import UserResponse, UserUpdate
from app.auth.service import update_user
from app.auth.dependencies import get_current_active_user
from app.users.schemas import UserPublicResponse
from app.users.service import get_user_public, get_all_users, deactivate_user
from app.core.config import settings

router = APIRouter(prefix="/users", tags=["users"])

UPLOAD_DIR = f"{settings.UPLOAD_DIR}/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get(
    "/",
    response_model=list[UserPublicResponse],
)
async def list_users(
    db: AsyncSession = Depends(get_db),
) -> list[UserPublicResponse]:
    users = await get_all_users(db)
    return [UserPublicResponse.model_validate(user) for user in users]


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    updated_user = await update_user(current_user, data, db)
    return UserResponse.model_validate(updated_user)


@router.post(
    "/me/avatar",
    response_model=UserResponse,
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
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

    updated_user = await update_user(
        current_user,
        UserUpdate(avatar_url=f"/uploads/avatars/{filename}"),
        db,
    )
    return UserResponse.model_validate(updated_user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_me(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await deactivate_user(current_user, db)


@router.get(
    "/{user_id}",
    response_model=UserPublicResponse,
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserPublicResponse:
    user = await get_user_public(user_id, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено",
        )
    return user