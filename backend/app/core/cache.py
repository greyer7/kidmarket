import json
from typing import Any

from app.core.redis import get_redis


async def get_cached(key: str) -> Any | None:
    
    redis = await get_redis()
    if redis is None:
        return None

    cached_value = await redis.get(key)
    if cached_value is None:
        return None

    return json.loads(cached_value)


async def set_cached(key: str, value: Any, ttl_seconds: int) -> None:
   
    redis = await get_redis()
    if redis is None:
        return

    await redis.set(key, json.dumps(value), ex=ttl_seconds)


async def invalidate_pattern(pattern: str) -> None:
    
    redis = await get_redis()
    if redis is None:
        return

    keys_to_delete = []
    async for key in redis.scan_iter(match=pattern):
        keys_to_delete.append(key)

    if keys_to_delete:
        await redis.delete(*keys_to_delete)