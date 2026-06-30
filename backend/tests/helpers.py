import uuid
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User


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


async def get_admin_token(client: AsyncClient, db_session: AsyncSession) -> str:
    email = unique_email()
    await client.post("/api/auth/register", json={
        "email": email,
        "password": "Test1234!",
        "full_name": "Admin User"
    })

    await db_session.execute(
        update(User).where(User.email == email).values(is_admin=True)
    )
    await db_session.commit()

    response = await client.post("/api/auth/login", data={
        "username": email,
        "password": "Test1234!"
    })
    return response.json()["access_token"]