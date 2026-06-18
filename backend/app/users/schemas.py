from datetime import datetime
from pydantic import BaseModel
from app.auth.schemas import UserResponse, UserUpdate

__all__ = ["UserResponse", "UserUpdate", "UserPublicResponse"]


class UserPublicResponse(BaseModel):
    id: int
    full_name: str
    avatar_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}