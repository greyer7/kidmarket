import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.auth.models import User
from app.listings.models import Listing, ListingStatus
from app.listings.service import get_listing_by_id
from app.payments.models import Payment, PaymentStatus

# Ключ Stripe встановлюється ОДИН РАЗ при завантаженні модуля -
# усі подальші виклики stripe.* автоматично використовують саме цей ключ.
stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_checkout_session(
    listing_id: int,
    buyer: User,
    db: AsyncSession,
) -> str:
    """
    Створює Stripe Checkout Session для купівлі конкретного оголошення.
    Повертає готовий URL сторінки оплати Stripe (куди фронтенд має
    зробити window.location.href, як ми вже робили з Google OAuth).
    """
    listing = await get_listing_by_id(listing_id, db)
    if listing is None:
        raise ValueError("Оголошення не знайдено")

    if listing.status != ListingStatus.active:
        raise ValueError("Це оголошення вже недоступне для купівлі")

    if listing.seller_id == buyer.id:
        raise ValueError("Не можна купити власне оголошення")

    # Stripe оперує сумами в НАЙМЕНШИХ одиницях валюти (копійках для UAH),
    # а не в "звичайних" гривнях - тому множимо на 100 і округлюємо до цілого.
    amount_in_cents = int(round(float(listing.price) * 100))

    checkout_session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "uah",
                    "unit_amount": amount_in_cents,
                    "product_data": {
                        "name": listing.title,
                        "description": listing.description[:500],
                    },
                },
                "quantity": 1,
            }
        ],
        success_url=f"{settings.FRONTEND_URL}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/payments/cancel",
        # metadata - довільні дані, які Stripe просто "зберігає при собі"
        # і поверне назад у webhook-події - так ми дізнаємось, ЯКЕ саме
        # оголошення і ХТО купував, коли прийде підтвердження оплати.
        metadata={
            "listing_id": str(listing.id),
            "buyer_id": str(buyer.id),
            "seller_id": str(listing.seller_id),
        },
    )

    payment = Payment(
        listing_id=listing.id,
        buyer_id=buyer.id,
        seller_id=listing.seller_id,
        stripe_checkout_session_id=checkout_session.id,
        amount=listing.price,
        currency="uah",
        status=PaymentStatus.pending,
    )
    db.add(payment)
    await db.flush()

    return checkout_session.url


async def handle_checkout_completed(checkout_session_id: str, db: AsyncSession) -> None:
    """
    Викликається з webhook-ендпоінту, коли Stripe підтверджує подію
    "checkout.session.completed" (оплата успішно пройшла).
    """
    result = await db.execute(
        select(Payment).where(Payment.stripe_checkout_session_id == checkout_session_id)
    )
    payment = result.scalar_one_or_none()

    if payment is None:
        # Це не повинно траплятись у нормальній роботі (кожна сесія
        # створюється НАМИ і одразу зберігається в БД), але про всяк
        # випадок - не кидаємо помилку, а просто виходимо, щоб не
        # "зламати" обробку webhook для Stripe (він очікує код 200).
        return

    if payment.status == PaymentStatus.completed:
        # Stripe інколи надсилає ОДНУ Й ТУ САМУ подію повторно
        # (гарантія доставки "at least once") - друга обробка не повинна
        # нічого зламати, тому просто виходимо, якщо вже оброблено.
        return

    payment.status = PaymentStatus.completed

    listing = await get_listing_by_id(payment.listing_id, db)
    if listing is not None:
        listing.status = ListingStatus.sold

    await db.flush()