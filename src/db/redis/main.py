import redis 

from config_reader import config

client = redis.Redis(
    host = config.redis.host,
    port = config.redis.port,
    decode_responses=True
)

ttl = 60 * 60 # 1 hour