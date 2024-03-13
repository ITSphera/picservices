from datetime import timedelta

from celery import Celery
from decouple import config
from fastapi import FastAPI
from redis import Redis
from starlette.staticfiles import StaticFiles

from src.images.middlewares.limit_requests import LimitRequestsMiddleware

# Redis settings
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB = config("REDIS_DB", default=0, cast=int)
REDIS_SERVER = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Celery settings
celery = Celery(
    "tasks",
    backend=config("REDIS_URL", default="redis://localhost:6379/0"),
    broker=config("REDIS_URL", default="redis://localhost:6379/0"),
)

celery.conf.update(
    broker_url=config("REDIS_URL", default="redis://localhost:6379/0"),
    result_backend=config("REDIS_URL", default="redis://localhost:6379/0"),
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
    result_expires=config("CELERY_RESULT_EXPIRES", default=3600, cast=int),
    broker_connection_retry_on_startup=True,
)

# FastAPI
app = FastAPI()
app.mount("/media", StaticFiles(directory="src/media"), name="media")

# Image settings
SERVICES = {
    "SVZ": {
        "avatar": {
            "dir": "svz/avatars",
            "width": config("SVZ_AVATAR_WIDTH", default=200, cast=int),
        },
        "recipe": {
            "dir": "svz/recipes",
            "width": config("SVZ_RECIPE_WIDTH", default=768, cast=int),
        },
    },
}
IMAGE_QUALITY = config("IMAGE_QUALITY", default=100, cast=int)

BASE_URL = config("BASE_URL", default="http://localhost:8000")

# Limit requests for API
MAX_REQUESTS = config("MAX_REQUESTS", default=5, cast=int)
TIME_WINDOW = timedelta(seconds=config("TIME_WINDOW", default=3, cast=int))
IP_BLACKLIST_DURATION = timedelta(
    minutes=config("IP_BLACKLIST_DURATION", default=60 * 24, cast=int)
)

app.add_middleware(
    LimitRequestsMiddleware,
    redis_server=REDIS_SERVER,
    max_requests=MAX_REQUESTS,
    time_window=TIME_WINDOW,
    blacklist_duration=IP_BLACKLIST_DURATION,
)
