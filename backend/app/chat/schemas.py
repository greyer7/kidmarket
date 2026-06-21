from datetime import datetime
from pydantic import BaseModel, Field
from app.users.schemas import UserPublicResponse


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    receiver_id: int
    listing_id: int


class MessageResponse(BaseModel):
    id: int
    content: str
    is_read: bool
    sender_id: int
    receiver_id: int
    listing_id: int
    sender: UserPublicResponse
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageShortResponse(BaseModel):
    id: int
    content: str
    is_read: bool
    sender: UserPublicResponse
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    listing_id: int
    other_user: UserPublicResponse
    last_message: MessageShortResponse
    unread_count: int

    model_config = {"from_attributes": False}