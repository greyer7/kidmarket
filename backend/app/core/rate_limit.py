from fastapi import HTTPException, Request, status

from app.core.redis import get_redis


def get_client_ip(request: Request) -> str:
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


async def check_rate_limit(
    request: Request,
    action: str,
    max_requests: int,
    window_seconds: int,
) -> None:
    
    redis = await get_redis()
    if redis is None:
        return

    client_ip = get_client_ip(request)
    redis_key = f"ratelimit:{action}:{client_ip}"

    current_count = await redis.incr(redis_key)

    if current_count == 1:
        await redis.expire(redis_key, window_seconds)

    if current_count > max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Забагато спроб. Спробуйте ще раз через {window_seconds} секунд."
            ),
        )