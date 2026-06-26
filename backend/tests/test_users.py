from tests.helpers import unique_email, get_token
import pytest
import uuid




@pytest.mark.anyio
async def test_get_users(client):
    response = await client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_me(client):
    token = await get_token(client)
    response = await client.get("/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data


@pytest.mark.anyio
async def test_update_me(client):
    token = await get_token(client)
    response = await client.patch("/api/users/me", json={
        "full_name": "Новое Имя"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Новое Имя"


@pytest.mark.anyio
async def test_get_me_unauthorized(client):
    response = await client.get("/api/users/me")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_get_user_by_id(client):
    token = await get_token(client)
    me = await client.get("/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    user_id = me.json()["id"]
    response = await client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id