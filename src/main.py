from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from src.images.router import router as images_router

from src.config import (
    REDIS_SERVER,
    MAX_REQUESTS,
    TIME_WINDOW,
    IP_BLACKLIST_DURATION,
)
from src.images.middlewares.limit_requests import LimitRequestsMiddleware

app = FastAPI()
app.include_router(images_router, prefix="/images")
app.mount("/media", StaticFiles(directory="src/media"), name="media")
app.add_middleware(
    LimitRequestsMiddleware,
    redis_server=REDIS_SERVER,
    max_requests=MAX_REQUESTS,
    time_window=TIME_WINDOW,
    blacklist_duration=IP_BLACKLIST_DURATION,
)


@app.get("/")
async def root():
    """
    Root endpoint
    :return:
    """

    return {"message": "Hello World"}
