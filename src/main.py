import redis.asyncio as redis
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
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

redis_client = redis.Redis(
    host="localhost", port=6379, db=0, decode_responses=True
)

# Include routers
app.include_router(images_router, prefix="/images")

# Mount media files
app.mount("/media", StaticFiles(directory="src/media"), name="media")


# Add exception handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = [
        {
            "loc": error["loc"],
            "msg": str(error["msg"]),  # Преобразуем msg в строку
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


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
