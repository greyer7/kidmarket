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


async def _count_keys(prefix: str) -> int:
    redis = await get_redis()
    count = 0
    async for _ in redis.scan_iter(match=f"{prefix}:*"):
        count += 1
    return count


async def _login_and_get_me(client, email: str, password: str) -> dict:
    login_response = await client.post("/api/auth/login", data={
        "username": email,
        "password": password,
    })
    token = login_response.json()["access_token"]

    me_response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    return me_response.json()


@pytest.mark.anyio
async def test_register_creates_unverified_user(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Unverified User",
    })

    me = await _login_and_get_me(client, email, "Test1234!")
    assert me["is_verified"] is False


@pytest.mark.anyio
async def test_register_creates_verification_token(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Test User",
    })

    assert await _count_keys("email_verify") == 1


@pytest.mark.anyio
async def test_verify_email_success(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Verify User",
    })

    token = await _extract_token_from_redis("email_verify")

    response = await client.post("/api/auth/verify-email", json={"token": token})
    assert response.status_code == 200

    me = await _login_and_get_me(client, email, "Test1234!")
    assert me["is_verified"] is True


@pytest.mark.anyio
async def test_verify_email_token_is_single_use(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Verify User",
    })
    token = await _extract_token_from_redis("email_verify")

    first_attempt = await client.post("/api/auth/verify-email", json={"token": token})
    assert first_attempt.status_code == 200

    second_attempt = await client.post("/api/auth/verify-email", json={"token": token})
    assert second_attempt.status_code == 400


@pytest.mark.anyio
async def test_verify_email_invalid_token(client):
    response = await client.post("/api/auth/verify-email", json={
        "token": "this-token-never-existed",
    })
    assert response.status_code == 400


@pytest.mark.anyio
async def test_resend_verification_generic_response(client):
    existing_email = unique_email()
    await client.post("/api/auth/register", json={
        "email": existing_email,
        "password": "Test1234!",
        "full_name": "Real User",
    })

    response_existing = await client.post(
        "/api/auth/resend-verification", json={"email": existing_email}
    )
    response_nonexistent = await client.post(
        "/api/auth/resend-verification", json={"email": "never_registered@example.com"}
    )

    assert response_existing.status_code == response_nonexistent.status_code == 200
    assert response_existing.json() == response_nonexistent.json()


@pytest.mark.anyio
async def test_resend_verification_does_not_reissue_for_already_verified(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Verify User",
    })

    token = await _extract_token_from_redis("email_verify")
    await client.post("/api/auth/verify-email", json={"token": token})

    assert await _count_keys("email_verify") == 0

    await client.post("/api/auth/resend-verification", json={"email": email})

    assert await _count_keys("email_verify") == 0