import pytest
from tests.helpers import unique_email
from app.core.redis import get_redis


async def _extract_token_from_redis(prefix: str) -> str:
    
    redis = await get_redis()
    keys = []
    async for key in redis.scan_iter(match=f"{prefix}:*"):
        keys.append(key)

    assert len(keys) == 1, f"Очікувався рівно 1 ключ з префіксом {prefix}, знайдено {len(keys)}"
    return keys[0].split(":", 1)[1]


@pytest.mark.anyio
async def test_forgot_password_existing_email(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Reset User",
    })

    response = await client.post("/api/auth/forgot-password", json={"email": email})

    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.anyio
async def test_forgot_password_nonexistent_email_same_response(client):
    existing_email = unique_email()
    await client.post("/api/auth/register", json={
        "email": existing_email,
        "password": "Test1234!",
        "full_name": "Real User",
    })

    response_existing = await client.post(
        "/api/auth/forgot-password", json={"email": existing_email}
    )
    response_nonexistent = await client.post(
        "/api/auth/forgot-password", json={"email": "totally_never_registered@example.com"}
    )

    assert response_existing.status_code == response_nonexistent.status_code == 200
    assert response_existing.json() == response_nonexistent.json()


@pytest.mark.anyio
async def test_reset_password_full_flow(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "OldPassword1!",
        "full_name": "Reset User",
    })

    await client.post("/api/auth/forgot-password", json={"email": email})
    token = await _extract_token_from_redis("password_reset")

    reset_response = await client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": "NewPassword1!",
    })
    assert reset_response.status_code == 200

    old_login = await client.post("/api/auth/login", data={
        "username": email,
        "password": "OldPassword1!",
    })
    assert old_login.status_code == 401

    new_login = await client.post("/api/auth/login", data={
        "username": email,
        "password": "NewPassword1!",
    })
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()


@pytest.mark.anyio
async def test_reset_password_token_is_single_use(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "OldPassword1!",
        "full_name": "Reset User",
    })

    await client.post("/api/auth/forgot-password", json={"email": email})
    token = await _extract_token_from_redis("password_reset")

    first_attempt = await client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": "NewPassword1!",
    })
    assert first_attempt.status_code == 200

    second_attempt = await client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": "AnotherPassword1!",
    })
    assert second_attempt.status_code == 400


@pytest.mark.anyio
async def test_reset_password_invalid_token(client):
    response = await client.post("/api/auth/reset-password", json={
        "token": "this-token-never-existed",
        "new_password": "NewPassword1!",
    })
    assert response.status_code == 400