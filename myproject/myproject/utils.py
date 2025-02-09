# tracking_utils.py
from django.core.cache import caches
from django.utils import timezone

def track_page_view(page_url, user_id=None):
    cache = caches['page_view_cache']
    
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