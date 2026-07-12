from datetime import datetime

from pydantic import BaseModel

from app.payments.models import PaymentStatus

class CheckoutSessionRequest(BaseModel):
    listing_id: int

class CheckoutSessionResponse(BaseModel):
    checkout_url: str

class PaymentResponse(BaseModel):
    id: int
    listing_id: int
    buyer_id: int
    seller_id: int
    amount: float
    currency: str
    status: PaymentStatus
    created_at: datetime


    model_config = {"from_attributes": True}
