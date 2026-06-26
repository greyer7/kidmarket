import pytest
from tests.helpers import unique_email, get_token
import uuid




@pytest.mark.anyio
async def test_register(client):
    email = unique_email()
    response = await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "Test User"
    assert "id" in data


@pytest.mark.anyio
async def test_register_duplicate_email(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Test User"
    })
    response = await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Test User"
    })
    assert response.status_code == 400


@pytest.mark.anyio
async def test_login(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Login User"
    })
    response = await client.post("/api/auth/login", data={
        "username": email,
        "password": "Test1234!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_wrong_password(client):
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Test User"
    })
    response = await client.post("/api/auth/login", data={
        "username": email,
        "password": "WrongPassword!"
    })
    assert response.status_code == 401