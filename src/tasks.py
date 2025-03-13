from src.config import celery
from src.images.image_handler import _process_image


@celery.task
def process_image(file: bytes, directory: str, image_width: int) -> str:
    """
    Process image from bytes and save it as a WEBP file with a specified width.
    """

    new_image_path = _process_image(file, directory, image_width)
    return str(new_image_path)
