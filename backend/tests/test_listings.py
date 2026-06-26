import pytest
import uuid
from tests.helpers import unique_email, get_token




@pytest.mark.anyio
async def test_create_listing(client):
    token = await get_token(client)
    response = await client.post("/api/listings/", json={
        "title": "Дитячий велосипед",
        "description": "В хорошому стані, майже новий",
        "price": 500,
        "condition": "new",
        "category": "transport"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Дитячий велосипед"
    assert data["price"] == 500
    assert "id" in data


@pytest.mark.anyio
async def test_get_listings(client):
    response = await client.get("/api/listings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_listing_by_id(client):
    token = await get_token(client)
    create = await client.post("/api/listings/", json={
        "title": "Іграшка для дітей",
        "description": "Нова іграшка в упаковці",
        "price": 100,
        "condition": "new",
        "category": "toys"
    }, headers={"Authorization": f"Bearer {token}"})
    listing_id = create.json()["id"]
    response = await client.get(f"/api/listings/{listing_id}")
    assert response.status_code == 200
    assert response.json()["id"] == listing_id


@pytest.mark.anyio
async def test_create_listing_unauthorized(client):
    response = await client.post("/api/listings/", json={
        "title": "Тест оголошення",
        "description": "Тест опис оголошення",
        "price": 100,
        "condition": "new",
        "category": "other"
    })
    assert response.status_code == 401