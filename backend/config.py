import os


def _get_cache_config():
    cache_type = os.getenv('CACHE_TYPE', 'RedisCache')
    redis_url = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0')

    if cache_type == 'RedisCache':
        try:
            import redis  # noqa: F401
            # Ping the server: fall back to an in-memory cache if it's down,
            # so @cache.cached()/@cache.memoize() decorators can't crash routes.
            client = redis.Redis.from_url(redis_url, socket_connect_timeout=1)
            client.ping()
        except Exception:
            cache_type = 'SimpleCache'
            redis_url = None

    return cache_type, redis_url


class Config:
    # Basic Flask + JWT secrets (fine for an academic/dev project)
    SECRET_KEY = 'This_is_the_secret_key_for_development'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-secret-key-change-in-production'

    # Use Redis when available; otherwise fall back to an in-memory cache.
    CACHE_TYPE, CACHE_REDIS_URL = _get_cache_config()
    CACHE_DEFAULT_TIMEOUT = 300

    # Where the CSV export files are written by the Celery task
    EXPORT_FOLDER = os.path.join(os.path.dirname(__file__), 'exports')

    # Mailhog SMTP (dev mail catcher). Read the inbox at http://localhost:8025
    # (that 8025 port is the web UI only -- SMTP delivery itself is on 1025)
    MAIL_HOST = os.getenv('MAIL_HOST', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '1025'))
    MAIL_SENDER = os.getenv('MAIL_SENDER', '22f3002042@ds.study.iitm.ac.in')

    # Celery uses Redis as broker (DB 1) and result backend (DB 2)
    CELERY = {
        'broker_url': 'redis://localhost:6379/1',
        'result_backend': 'redis://localhost:6379/2',
        'task_ignore_result': False,
    }


config = Config()
