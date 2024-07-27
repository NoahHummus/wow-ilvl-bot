import time

cache = {}
CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)

def get_cached_data(key):
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
    return None

def set_cached_data(key, data):
    cache[key] = (data, time.time())