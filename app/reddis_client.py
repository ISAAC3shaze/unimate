import redis
import os

redis_url = os.getenv("redis://default:KYWpYpNbBdjWfbcNDioOkwDCAgIicEaE@mainline.proxy.rlwy.net:31827")

r = redis.from_url(redis_url, decode_responses=True)