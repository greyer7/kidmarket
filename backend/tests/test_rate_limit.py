import pytest
from tests.helpers import unique_email


@pytest.mark.anyio
async def test_login_rate_limit_blocks_after_max_attempts(client):
    for _ in range(5):
        response = await client.post("/api/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "wrong_password",
        })
        assert response.status_code == 401

    sixth_response = await client.post("/api/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrong_password",
    })
    assert sixth_response.status_code == 429


@pytest.mark.anyio
async def test_register_rate_limit_blocks_after_max_attempts(client):
    for _ in range(3):
        response = await client.post("/api/auth/register", json={
            "email": unique_email(),
            "password": "Test1234!",
            "full_name": "Rate Limit Test",
        })
        assert response.status_code == 201

    fourth_response = await client.post("/api/auth/register", json={
        "email": unique_email(),
        "password": "Test1234!",
        "full_name": "Rate Limit Test",
    })
    assert fourth_response.status_code == 429


@pytest.mark.anyio
async def test_rate_limits_are_independent_per_endpoint(client):
    for _ in range(5):
        await client.post("/api/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "wrong_password",
        })

    blocked = await client.post("/api/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrong_password",
    })
    assert blocked.status_code == 429

    forgot_password_response = await client.post(
        "/api/auth/forgot-password", json={"email": "someone@example.com"}
    )
    assert forgot_password_response.status_code == 200