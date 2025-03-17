from datetime import timedelta

from celery import Celery
from decouple import config
from redis.asyncio import Redis

# Redis settings
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

# Celery settings
celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
celery.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
    result_expires=config("CELERY_RESULT_EXPIRES", default=3600, cast=int),
    broker_connection_retry_on_startup=True,
)


# Настройки изображений
class ImageServiceConfig:
    dir: str
    width: int


SERVICES: dict[str, dict[str, ImageServiceConfig]] = {
    "SVZ": {
        "avatar": {
            "dir": "svz/avatars",
            "width": config("SVZ_AVATAR_WIDTH", default=200, cast=int),
        },
        "recipe_preview": {
            "dir": "svz/recipes/previews",
            "width": config("SVZ_RECIPE_WIDTH", default=768, cast=int),
        },
        "recipe_images": {
            "dir": "svz/recipes/images",
            "width": config("SVZ_POST_IMAGE_WIDTH", default=768, cast=int),
        },
    },
    "test": {
        "test": {
            "dir": "test",
            "width": config("SVZ_AVATAR_WIDTH", default=200, cast=int),
        },
    },
}

IMAGE_QUALITY = config("IMAGE_QUALITY", default=100, cast=int)
MAX_IMAGE_HEIGHT = config("MAX_IMAGE_HEIGHT", default=1080, cast=int)

# Базовый URL
BASE_URL = config("BASE_URL", default="http://localhost:8000")

# Ограничение запросов API
MAX_REQUESTS = config("MAX_REQUESTS", default=5, cast=int)
TIME_WINDOW = timedelta(seconds=config("TIME_WINDOW", default=3, cast=int))
IP_BLACKLIST_DURATION = timedelta(
    minutes=config("IP_BLACKLIST_DURATION", default=1440, cast=int)
)
