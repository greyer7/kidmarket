from datetime import datetime
from pydantic import BaseModel, Field
from app.users.schemas import UserPublicResponse


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, min_length=10, max_length=1000)
    listing_id: int


class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: str | None
    reviewer_id: int
    seller_id: int
    listing_id: int
    reviewer: UserPublicResponse
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewShortResponse(BaseModel):
    id: int
    rating: int
    comment: str | None
    reviewer: UserPublicResponse
    created_at: datetime

    model_config = {"from_attributes": True}


class SellerRatingResponse(BaseModel):
    seller_id: int
    average_rating: float
    total_reviews: int