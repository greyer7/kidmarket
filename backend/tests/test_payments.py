import hashlib
import hmac
import json
import time

import pytest
from sqlalchemy import select

from tests.helpers import get_token
from app.core.config import settings
from app.listings.models import Listing
from app.payments.models import Payment, PaymentStatus


async def _create_listing(client, token: str, price: float = 500) -> int:
    response = await client.post("/api/listings/", json={
        "title": "Тестовий товар",
        "description": "Опис для тестування платежів",
        "price": price,
        "condition": "new",
        "category": "toys",
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()["id"]


def _build_stripe_signature_header(payload_bytes: bytes, secret: str) -> str:
    
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload_bytes.decode()}"
    signature = hmac.new(
        secret.encode(), signed_payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


class FakeStripeSession:
    """Підміняє реальний stripe.checkout.Session.create - без мережі до Stripe."""
    def __init__(self, id: str, url: str):
        self.id = id
        self.url = url


@pytest.mark.anyio
async def test_create_checkout_session_requires_auth(client):
    response = await client.post(
        "/api/payments/create-checkout-session", json={"listing_id": 1}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_checkout_session_listing_not_found(client):
    token = await get_token(client)
    response = await client.post(
        "/api/payments/create-checkout-session",
        json={"listing_id": 99999999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_create_checkout_session_cannot_buy_own_listing(client):
    seller_token = await get_token(client)
    listing_id = await _create_listing(client, seller_token)

    response = await client.post(
        "/api/payments/create-checkout-session",
        json={"listing_id": listing_id},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert response.status_code == 400
    assert "власне" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_create_checkout_session_already_sold(client, db_session):
    seller_token = await get_token(client)
    buyer_token = await get_token(client)
    listing_id = await _create_listing(client, seller_token)

    # Напряму позначаємо товар проданим в БД (імітуємо стан "уже купили").
    listing = await db_session.get(Listing, listing_id)
    listing.status = "sold"
    await db_session.commit()

    response = await client.post(
        "/api/payments/create-checkout-session",
        json={"listing_id": listing_id},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_create_checkout_session_success(client, db_session, monkeypatch):
   
    def fake_create(**kwargs):
        return FakeStripeSession(id="cs_test_fake123", url="https://checkout.stripe.com/fake")

    monkeypatch.setattr(
        "app.payments.service.stripe.checkout.Session.create", fake_create
    )

    seller_token = await get_token(client)
    buyer_token = await get_token(client)
    listing_id = await _create_listing(client, seller_token, price=250)

    response = await client.post(
        "/api/payments/create-checkout-session",
        json={"listing_id": listing_id},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )

    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://checkout.stripe.com/fake"

    result = await db_session.execute(
        select(Payment).where(Payment.stripe_checkout_session_id == "cs_test_fake123")
    )
    payment = result.scalar_one()
    assert payment.listing_id == listing_id
    assert payment.status == PaymentStatus.pending
    assert float(payment.amount) == 250


@pytest.mark.anyio
async def test_webhook_invalid_signature_rejected(client):
    payload = json.dumps({"type": "checkout.session.completed", "data": {"object": {"id": "cs_fake"}}})

    response = await client.post(
        "/api/payments/webhook",
        content=payload,
        headers={"stripe-signature": "t=123,v1=totally_fake_signature"},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_webhook_valid_signature_completes_payment(client, db_session, monkeypatch):
    
    def fake_create(**kwargs):
        return FakeStripeSession(id="cs_test_webhook456", url="https://checkout.stripe.com/fake2")

    monkeypatch.setattr(
        "app.payments.service.stripe.checkout.Session.create", fake_create
    )

    seller_token = await get_token(client)
    buyer_token = await get_token(client)
    listing_id = await _create_listing(client, seller_token, price=100)

    await client.post(
        "/api/payments/create-checkout-session",
        json={"listing_id": listing_id},
        headers={"Authorization": f"Bearer {buyer_token}"},
    )

    event_payload = json.dumps({
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test_webhook456"}},
    }).encode()

    signature_header = _build_stripe_signature_header(
        event_payload, settings.STRIPE_WEBHOOK_SECRET
    )

    response = await client.post(
        "/api/payments/webhook",
        content=event_payload,
        headers={
            "stripe-signature": signature_header,
            "content-type": "application/json",
        },
    )
    assert response.status_code == 200

    payment_result = await db_session.execute(
        select(Payment).where(Payment.stripe_checkout_session_id == "cs_test_webhook456")
    )
    payment = payment_result.scalar_one()
    assert payment.status == PaymentStatus.completed

    listing = await db_session.get(Listing, listing_id)
    await db_session.refresh(listing)
    assert listing.status == "sold"