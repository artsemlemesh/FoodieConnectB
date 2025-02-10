# tracking_utils.py
from django.core.cache import caches
from django.utils import timezone
import time

ONLINE_USERS_KEY = "online_users"  # Key for tracking online users

cache = caches['page_view_cache']

def track_page_view(page_url, user_id=None):
    
    #increment total page view count
    cache_key = f'page_view:{page_url}'

    # Check if the key exists, then increment, otherwise set it to 1
    if cache.get(cache_key) is None:
        cache.add(cache_key, 0)
    else:
        cache.incr(cache_key)

    #track daily views (reset every 24 hours)
    daily_cache_key = f'page_view_daily:{page_url}:{timezone.now().strftime("%Y-%m-%d")}'

    if cache.get(daily_cache_key) is None:
        cache.add(daily_cache_key, 0, timeout=60*60*24)  # 24-hour timeout
    else:
        cache.incr(daily_cache_key)

    # Optionally, track unique user visits with a timestamp
    if user_id:
        timestamp_key = f'page_view_timestamp:{page_url}:{user_id}'
        cache.set(timestamp_key, timezone.now(), timeout=60*60)  # 1-hour timeout

import logging
logger = logging.getLogger(__name__)

def mark_user_online(user_id, timeout=300):
    """
    Mark a user as online.
    
    :param user_id: Unique user identifier (e.g., user.id or session id)
    :param timeout: Time in seconds until the user is considered offline (default: 5 minutes)
    """

    if not user_id:
        logger.info("No user_id provided, returning early.")
        return
    
    # logger.info(f"Marking user {user_id} as online.")
    current_time = int(time.time())
    # logger.info(f"Current time: {current_time}")

    cache.set(f'{ONLINE_USERS_KEY}:{user_id}', current_time, timeout)
    # logger.info(f"User {user_id} marked as online at {current_time}")

def get_online_users_count():
    """
    Get the count of online users by counting all keys in Redis that match 'online_users:*'
    """

    keys = cache.keys(f'{ONLINE_USERS_KEY}:*')
    # logger.info(f"Keys in Redis: {keys}")

    # logger.info(f"Found {len(keys)} online users in Redis.")

    return len(keys)

