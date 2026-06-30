import pytest
from tests.helpers import get_token, get_admin_token


@pytest.mark.anyio
async def test_admin_stats_requires_admin(client, db_session):
    token = await get_token(client)
    response = await client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_admin_stats_unauthorized(client):
    response = await client.get("/api/admin/stats")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_admin_stats_success(client, db_session):
    admin_token = await get_admin_token(client, db_session)
    response = await client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "active_users" in data
    assert "total_listings" in data
    assert "active_listings" in data
    assert "sold_listings" in data


@pytest.mark.anyio
async def test_admin_get_users(client, db_session):
    admin_token = await get_admin_token(client, db_session)
    response = await client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_admin_get_users_forbidden_for_regular_user(client):
    token = await get_token(client)
    response = await client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_admin_block_user(client, db_session):
    admin_token = await get_admin_token(client, db_session)
    regular_token = await get_token(client)

    me_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    user_id = me_response.json()["id"]

    response = await client.patch(
        f"/api/admin/users/{user_id}/active",
        params={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.anyio
async def test_admin_block_nonexistent_user(client, db_session):
    admin_token = await get_admin_token(client, db_session)
    response = await client.patch(
        "/api/admin/users/999999/active",
        params={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_admin_get_listings(client, db_session):
    admin_token = await get_admin_token(client, db_session)
    response = await client.get(
        "/api/admin/listings",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_admin_delete_listing(client, db_session):
    admin_token = await get_admin_token(client, db_session)
    seller_token = await get_token(client)

    create = await client.post("/api/listings/", json={
        "title": "Тестове оголошення для видалення",
        "description": "Опис тестового оголошення",
        "price": 200,
        "condition": "new",
        "category": "toys",
    }, headers={"Authorization": f"Bearer {seller_token}"})
    listing_id = create.json()["id"]

    response = await client.delete(
        f"/api/admin/listings/{listing_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    check = await client.get(f"/api/listings/{listing_id}")
    assert check.status_code == 404


@pytest.mark.anyio
async def test_admin_delete_nonexistent_listing(client, db_session):
    admin_token = await get_admin_token(client, db_session)
    response = await client.delete(
        "/api/admin/listings/999999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404