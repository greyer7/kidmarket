from datetime import datetime
from pydantic import BaseModel


class AdminUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminListingResponse(BaseModel):
    id: int
    title: str
    price: float
    status: str
    category: str
    seller_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_listings: int
    active_listings: int
    sold_listings: int