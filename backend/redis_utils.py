import redis
import logging

# Initialize logger
logger = logging.getLogger("app")

def ping_redis(config):
    redis_url = config['REDIS_URL']
    try:
        # Create a Redis client
        rs = redis.from_url(redis_url)
        # Use the ping command to check the connection
        response = rs.ping()
        return response
    except Exception as e:
        # Handle any exceptions that may occur during the connection check
        logger.error(f"Connection check failed: {e}")
        return False
