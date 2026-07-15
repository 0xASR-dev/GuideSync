from extensions import cache



KEY_OPEN_TREKS = 'treks_open_list'       
KEY_ADMIN_DASHBOARD = 'admin_dashboard'  


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
    delete(KEY_OPEN_TREKS)
    delete(KEY_ADMIN_DASHBOARD)
