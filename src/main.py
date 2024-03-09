from fastapi import FastAPI, File, UploadFile

from .tasks import process_image
from .config import SERVICES

app = FastAPI()


@app.get("/")
async def root():
    """
    Root endpoint
    :return:
    """
    return {"message": "Hello World"}


@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...), service: str = SERVICES, target_type: str = str
):
    """
    Upload image
    :param file:
    :return:
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
    task = process_image.delay(file, target_dir, width)

    return {"task_id": task.id, "message": "Image processing started"}
