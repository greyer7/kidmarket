from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis | None = None


async def get_redis() -> Redis:
    return redis_client


async def init_redis() -> None:
    global redis_client
    redis_client = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None