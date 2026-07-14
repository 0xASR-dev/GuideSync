from extensions import cache

# ---------------------------------------------------------------------------
# Tiny helper around Redis cache.
# We use fixed key names so we can delete (invalidate) them on write actions.
#
# Every call is wrapped in try/except: if the Redis server is not running,
# the app should still work (it just skips the cache instead of crashing).
# ---------------------------------------------------------------------------

KEY_OPEN_TREKS = 'treks_open_list'       # list of Open treks (for trekkers)
KEY_ADMIN_DASHBOARD = 'admin_dashboard'  # admin count numbers


def get(key):
    try:
        return cache.get(key)
    except Exception:
        return None


def set(key, value, timeout=300):
    try:
        cache.set(key, value, timeout=timeout)
    except Exception:
        pass


def delete(key):
    try:
        cache.delete(key)
    except Exception:
        pass


def clear_all_trek_caches():
    """Call this on any booking / trek change so users see fresh data.

    Per-user booking caches use @cache.memoize() and are invalidated
    separately via cache.delete_memoized() at the call site.
    """
    delete(KEY_OPEN_TREKS)
    delete(KEY_ADMIN_DASHBOARD)
