from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    avatar_url: str | None = Field(default=None)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: datetime