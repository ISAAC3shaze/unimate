import redis
import os

redis_url = os.getenv("REDIS_URL")

if not redis_url:
    raise Exception("❌ REDIS_URL not set in environment")

r = redis.from_url(redis_url, decode_responses=True)

print("✅ Redis connected successfully")