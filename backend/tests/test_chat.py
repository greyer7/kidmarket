import pytest
from tests.helpers import get_token


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
async def test_send_message(client):
    seller_token = await get_token(client)
    buyer_token = await get_token(client)

    listing = await create_listing(client, seller_token)

    response = await client.post("/api/chat/messages", json={
        "listing_id": listing["id"],
        "receiver_id": listing["seller_id"],
        "content": "Привіт, чи ще продається?"
    }, headers={"Authorization": f"Bearer {buyer_token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Привіт, чи ще продається?"


@pytest.mark.anyio
async def test_get_conversations(client):
    token = await get_token(client)
    response = await client.get("/api/chat/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_send_message_unauthorized(client):
    response = await client.post("/api/chat/messages", json={
        "listing_id": 1,
        "receiver_id": 1,
        "content": "Без авторизації"
    })
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_conversation(client):
    seller_token = await get_token(client)
    buyer_token = await get_token(client)

    listing = await create_listing(client, seller_token)
    seller_id = listing["seller_id"]
    listing_id = listing["id"]

    await client.post("/api/chat/messages", json={
        "listing_id": listing_id,
        "receiver_id": seller_id,
        "content": "Привіт, є питання!"
    }, headers={"Authorization": f"Bearer {buyer_token}"})

    response = await client.get(
        f"/api/chat/conversations/{seller_id}/{listing_id}",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 200