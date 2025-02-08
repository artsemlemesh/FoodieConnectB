# tracking_utils.py
from django.core.cache import caches
from django.utils import timezone

def track_page_view(page_url, user_id=None):
    cache = caches['page_view_cache']
    cache_key = f'page_view:{page_url}'

    # Check if the key exists, then increment, otherwise set it to 1
    if cache.get(cache_key) is None:
        cache.set(cache_key, 1)
    else:
        cache.incr(cache_key)

    # Optionally, track unique user visits with a timestamp
    if user_id:
        timestamp_key = f'page_view_timestamp:{page_url}:{user_id}'
        cache.set(timestamp_key, timezone.now(), timeout=60*60)  # 1-hour timeout