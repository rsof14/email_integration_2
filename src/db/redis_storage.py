from redis.asyncio import Redis
from core.config import redis_config


def get_redis():
    redis = Redis(host=redis_config.host, port=redis_config.port, db=0)
    return redis