from src.config import celery
from src.images.image_handler import image_handler


@celery.task
def process_image(file: bytes, direrctory: str, image_width: int) -> str:
    """
    Process image from bytes and save it as a WEBP file with a specified width.

    Args:
        file (bytes): The image file in bytes.
        direrctory (str): The directory where the image will be saved.
        image_width (int): The width of the resized image.

    Returns:
        Path: The file path of the saved image.
    """

    return str(image_handler(file, direrctory, image_width))
