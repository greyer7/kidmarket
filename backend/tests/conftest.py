import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

TEST_DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture
async def client():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    session = TestingSessionLocal()

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    await session.close()
    app.dependency_overrides.clear()
    await engine.dispose()