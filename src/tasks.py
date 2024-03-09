from pathlib import Path

from celery import Celery

from src.images.image_handler import image_handler

celery = Celery("tasks", broker="redis://localhost:6379/0")


@celery.task
def process_image(file: bytes, direrctory: str, image_width: int) -> Path:
    """
    Process image
    :param image_width: Image width
    :param direrctory: Save directory
    :param file: Image file
    :return:
    """

    return image_handler(file, direrctory, image_width)
