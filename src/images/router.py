import asyncio
from pathlib import Path
from celery.result import AsyncResult
from typing import Any, Union
from PIL import Image
from io import BytesIO

from fastapi import File, UploadFile, Depends

from fastapi import APIRouter
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .models import UploadData
from src.tasks import process_image
from src.config import SERVICES, celery, BASE_URL


router = APIRouter()


@router.post("/upload")
async def upload_image(
    upload_data: UploadData = Depends(), file: UploadFile = File(...)
) -> Union[dict, Any]:
    """
    Upload image to the server
    Args:
        upload_data (UploadData): The service and target type for image processing.
        file (UploadFile): The image file to be uploaded.
    Returns:
        dict: A dictionary containing the task ID and message.
    """
    service = upload_data.service
    target_type = upload_data.target_type

    if service not in SERVICES:
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": f"Service '{service}' not found"},
        )
    if target_type not in SERVICES[service]:
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": f"Target type '{target_type}' not found for service '{service}'"
            },
        )

    file: bytes = await file.read()
    target_dir: str = SERVICES[service][target_type]["dir"]
    width: int = SERVICES[service][target_type]["width"]

    try:
        # Проверить что файл является изображением
        with Image.open(BytesIO(file)) as _:
            task: asyncio.Task = process_image.delay(file, target_dir, width)
    except Exception:
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Error processing image: File is not an image"},
        )

    return {"task_id": task.id, "message": "Image processing started"}


@router.get("/status/{task_id}")
async def get_status(task_id: str) -> dict:
    """
    Get status of a task

    Args:
        task_id (str): The ID of the task.

    Returns:
        dict: A dictionary containing the status of the task.
    """

    task: AsyncResult = AsyncResult(task_id, app=celery)

    file_url = None

    if task.state == "SUCCESS":
        result = task.get()
        if result:
            file_path = Path(result).relative_to("src/media/")
            file_url = f"{BASE_URL}/media/{file_path}"

    return {"task_id": task_id, "status": task.state, "result": file_url}
