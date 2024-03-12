from celery import Celery
from decouple import config
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

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

app = FastAPI()
app.mount("/media", StaticFiles(directory="src/media"), name="media")


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

BASE_URL = config("BASE_URL", default="http://localhost:8000")
