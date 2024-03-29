import asyncio
from pathlib import Path
from celery.result import AsyncResult

from fastapi import File, UploadFile

from fastapi import APIRouter
from src.tasks import process_image
from src.config import SERVICES, celery, BASE_URL


router = APIRouter()


@router.post("/upload")
async def upload_image(
    service: str, target_type: str, file: UploadFile = File(...)
) -> dict:
    """
    Upload image to the server

    Args:
        file (UploadFile): The image file to be uploaded.
        service (str): The service to use for image processing.
        target_type (str): The target type for image processing.

    Returns:
        dict: A dictionary containing the task ID and message.
    """

    if service not in SERVICES:
        return {"error": f"Service '{service}' not found"}
    if target_type not in SERVICES[service]:
        return {
            "error": f"Target type '{target_type}' not found for service '{service}'"
        }

    file: bytes = await file.read()
    target_dir: str = SERVICES[service][target_type]["dir"]
    width: int = SERVICES[service][target_type]["width"]
    task: asyncio.Task = process_image.delay(file, target_dir, width)

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
