from celery import Celery
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

celery = Celery(
    "tasks", backend="redis://localhost:6379/0", broker="redis://localhost:6379/0"
)

celery.conf.update(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0",
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)

app = FastAPI()
app.mount("/media", StaticFiles(directory="src/media"), name="media")


SERVICES = {
    "SVZ": {
        "avatar": {"dir": "svz/avatars", "width": 200},
        "recipe": {"dir": "svz/recipes", "width": 768},
    },
}

BASE_URL = "http://127.0.0.1:8000"
