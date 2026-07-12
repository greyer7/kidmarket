import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.payments.schemas import CheckoutSessionRequest, CheckoutSessionResponse
from app.payments.service import create_checkout_session, handle_checkout_completed

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/create-checkout-session",
    response_model=CheckoutSessionResponse,
)
async def create_session(
    data: CheckoutSessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutSessionResponse:
    try:
        checkout_url = await create_checkout_session(data.listing_id, current_user, db)
        return CheckoutSessionResponse(checkout_url=checkout_url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Приймає webhook-події від Stripe.
    """
    payload = await request.body()
    signature_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        checkout_session_id = event["data"]["object"]["id"]
        await handle_checkout_completed(checkout_session_id, db)

    return {"status": "ok"}