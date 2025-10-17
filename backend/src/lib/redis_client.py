import os
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Redis settings object to be imported by the worker and the main app
redis_settings = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)

# Global pool for the FastAPI app
_redis_pool = None

async def get_redis_pool() -> ArqRedis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = await create_pool(redis_settings)
    return _redis_pool

async def close_redis_pool():
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None

async def get_redis() -> ArqRedis:
    """FastAPI dependency to get the Redis pool."""
    return await get_redis_pool()