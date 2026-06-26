import pytest
import uuid


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@gmail.com"


async def get_token(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Test User"
    })
    response = await client.post("/api/auth/login", data={
        "username": email,
        "password": "Test1234!"
    })
    return response.json()["access_token"]


async def create_listing(client, token):
    response = await client.post("/api/listings/", json={
        "title": "Дитячий велосипед",
        "description": "В хорошому стані, майже новий",
        "price": 500,
        "condition": "new",
        "category": "transport"
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()


@pytest.mark.anyio
async def test_create_review(client):
    seller_token = await get_token(client)
    buyer_token = await get_token(client)

    listing = await create_listing(client, seller_token)

    seller_id = listing["seller_id"]
    listing_id = listing["id"]

    response = await client.post("/api/reviews/", json={
        "rating": 5,
        "comment": "Відмінний продавець!",
        "listing_id": listing_id
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["seller_id"] == seller_id


@pytest.mark.anyio
async def test_create_review_own_listing(client):
    token = await get_token(client)
    listing = await create_listing(client, token)

    response = await client.post("/api/reviews/", json={
        "rating": 5,
        "comment": "Свій відгук",
        "listing_id": listing["id"]
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


@pytest.mark.anyio
async def test_get_listing_reviews(client):
    token = await get_token(client)
    listing = await create_listing(client, token)

    response = await client.get(f"/api/reviews/listings/{listing['id']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_create_review_unauthorized(client):
    token = await get_token(client)
    listing = await create_listing(client, token)

    response = await client.post("/api/reviews/", json={
        "rating": 5,
        "comment": "Без авторизації",
        "listing_id": listing["id"]
    })
    assert response.status_code == 401