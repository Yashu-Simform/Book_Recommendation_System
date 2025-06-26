from redis.asyncio import Redis
from app.core.config import settings

class RedisDB(Redis):
    def __init__(self, *, db=0, **kwargs):
        return super().__init__(host=settings.cache_host, port=settings.cache_port, db=0, **kwargs)

app_cache = RedisDB(db=0)
token_blacklist_cache = RedisDB(db=1)