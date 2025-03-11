from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.config import IP_BLACKLIST_DURATION
from src.config import MAX_REQUESTS
from src.config import REDIS_SERVER
from src.config import TIME_WINDOW
from src.images.middlewares.limit_requests import LimitRequestsMiddleware
from src.images.router import router as images_router

ORIGIN = [
    "*",
]

app = FastAPI(title="Image Processing API", version="1.0.0")

# Include routers
app.include_router(images_router, prefix="/images")

# Mount media files
app.mount("/media", StaticFiles(directory="src/media"), name="media")

# Add middleware
app.add_middleware(
    LimitRequestsMiddleware,
    redis_server=REDIS_SERVER,
    max_requests=MAX_REQUESTS,
    time_window=TIME_WINDOW,
    blacklist_duration=IP_BLACKLIST_DURATION,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint

    :return:
        A dictionary with a message
    """

    return {"message": "Hello World"}
