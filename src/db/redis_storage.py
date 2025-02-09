from redis.asyncio import Redis
from core.config import RedisConfig


conf = RedisConfig()


async def get_redis() -> Redis:
    redis = Redis(host="0.0.0.0", port=conf.port, db=0)
    return redis