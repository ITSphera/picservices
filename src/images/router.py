import asyncio
import logging
from typing import Any
from typing import Dict
from typing import Union

from celery.result import AsyncResult
from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import status
from fastapi import UploadFile
from pydantic import ValidationError
from starlette.responses import JSONResponse

from .models import UploadData
from .utils import get_file_url
from .validators import validate_image
from src.base import text_codes
from src.config import celery
from src.tasks import process_image

router = APIRouter()

logger = logging.getLogger(__name__)


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

    try:
        target_info = upload_data.target_info
        file_content = await file.read()

        await validate_image(file_content)

        task = process_image.delay(
            file_content, target_info["dir"], target_info["width"]
        )

        return {
            "task_id": task.id,
            "message": text_codes.IMAGE_PROCESSING_STARTED,
        }

    except ValidationError as e:
        # Обработка ошибок валидации из Pydantic
        logger.error("Error processing image: %s", e, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": str(e)},
        )
    except HTTPException as e:
        # Переброс HTTP исключений
        logger.error("Error processing image: %s", e, exc_info=True)
        return JSONResponse(
            status_code=e.status_code, content={"error": e.detail}
        )
    except Exception as e:
        # Обработка неожиданных ошибок
        logger.error("Error processing image: %s", e, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": f"{text_codes.ERROR_UNPROCESSABLE_ENTITY}: {str(e)}"
            },
        )


@router.get("/status/{task_id}", response_model=Dict[str, Any])
async def get_status(task_id: str) -> dict:
    """
    Get status of image processing

    Args:
        task_id (str): The task ID of the image processing task.

    Returns:
        dict: A dictionary containing the task ID, status, and result URL.
    """

    try:
        task = AsyncResult(task_id, app=celery)
        file_url = None

        # Если задача выполнена успешно, извлекаем результат в отдельном потоке
        if task.state == "SUCCESS":
            # Оборачивание блокирующего вызова в asyncio.to_thread
            result = await asyncio.to_thread(task.get)

            if result:
                file_url = get_file_url(result)

        return {"task_id": task_id, "status": task.state, "result": file_url}
    except Exception as e:
        logger.error(
            "Error getting status for task %s: %s", task_id, e, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=text_codes.ERROR_UNPROCESSABLE_ENTITY,
        )
