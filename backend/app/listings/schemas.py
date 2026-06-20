from datetime import datetime
from pydantic import BaseModel, Field
from app.listings.models import ListingStatus, ListingCondition
from app.users.schemas import UserPublicResponse


class ListingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10)
    price: float = Field(gt=0)
    condition: ListingCondition
    category: str = Field(min_length=2, max_length=100)
    image_urls: str | None = Field(default=None)


class ListingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, min_length=10)
    price: float | None = Field(default=None, gt=0)
    condition: ListingCondition | None = Field(default=None)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    image_urls: str | None = Field(default=None)
    status: ListingStatus | None = Field(default=None)


class ListingResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    status: ListingStatus
    condition: ListingCondition
    category: str
    image_urls: str | None
    seller_id: int
    seller: UserPublicResponse
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ListingShortResponse(BaseModel):
    id: int
    title: str
    price: float
    status: ListingStatus
    condition: ListingCondition
    category: str
    image_urls: str | None
    seller_id: int
    created_at: datetime

    model_config = {"from_attributes": True}