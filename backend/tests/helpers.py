import uuid
from httpx import AsyncClient


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@gmail.com"


async def get_token(client: AsyncClient) -> str:
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