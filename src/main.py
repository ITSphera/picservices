from decouple import config
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles

from src.config import IP_BLACKLIST_DURATION
from src.config import MAX_REQUESTS
from src.config import redis_client
from src.config import TIME_WINDOW
from src.images.middlewares.limit_requests import LimitRequestsMiddleware
from src.images.router import router as images_router

ORIGINS = config("CORS_ORIGINS", default="*", cast=lambda v: v.split(","))

app = FastAPI(title="Image Processing API", version="1.0.0")

# Подключение маршрутов
app.include_router(images_router, prefix="/images")

# Раздача статических файлов
app.mount("/media", StaticFiles(directory="src/media"), name="media")


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = [
        {
            "loc": error["loc"],
            "msg": str(error["msg"]),
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


# Добавление middleware
app.add_middleware(
    LimitRequestsMiddleware,
    redis_server=redis_client,
    max_requests=MAX_REQUESTS,
    time_window=TIME_WINDOW,
    blacklist_duration=IP_BLACKLIST_DURATION,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
