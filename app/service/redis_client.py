import redis
from fastapi import HTTPException

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

def get_cache(key: str):
    return redis_client.get(key)

def set_cache(key: str, value: str, ttl: int = 3600):
    redis_client.setex(key, ttl, value)
