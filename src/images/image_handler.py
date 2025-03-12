import asyncio
import logging
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image

from src.config import IMAGE_QUALITY
from src.config import MAX_IMAGE_HEIGHT

logger = logging.getLogger(__name__)


async def image_handler(file: bytes, directory: str, image_width: int) -> Path:
    """
    Asyncronously processes an image and returns the path to the saved image.

    Args:
        file (bytes): The image file in bytes.
        directory (str): The directory where the image will be saved.
        image_width (int): The width of the resized image.

    Returns:
        Path: The file path of the saved image.
    """

    return await asyncio.to_thread(
        _process_image, file, directory, image_width
    )


def _process_image(file: bytes, directory: str, image_width: int) -> Path:
    """
    Performs the actual image processing in a separate thread.

    Args:
        file (bytes): The image file in bytes.
        directory (str):A catalogue for saving images.
        image_width (int): The width of the image after resizing.

    Returns:
        Path: The file path of the saved image.
    """

    try:
        with Image.open(BytesIO(file)) as image:
            if not getattr(image, "format", None):
                raise ValueError("Некорректный формат изображения")

            if image.mode != "RGB":
                image = image.convert("RGB")

            aspect_ratio = image.height / image.width
            new_height = int(image_width * aspect_ratio)

            resample_method = Image.LANCZOS
            if image.width > image_width * 4:  # Для очень больших изображений
                resample_method = Image.BILINEAR

            resized_image = image.resize(
                (image_width, new_height), resample=resample_method
            )

            if new_height > MAX_IMAGE_HEIGHT:
                top = (new_height - MAX_IMAGE_HEIGHT) // 2
                resized_image = resized_image.crop(
                    (0, top, image_width, top + MAX_IMAGE_HEIGHT)
                )

            safe_directory = Path(directory).name
            output_dir = Path("src/media") / safe_directory
            output_dir.mkdir(parents=True, exist_ok=True)

            file_name = f"{uuid4()}.webp"
            output_path = output_dir / file_name

            resized_image.save(
                output_path,
                "WEBP",
                quality=IMAGE_QUALITY,
                method=6,
                lossless=False,
                exact=False,
            )

            return output_path
    except Exception as e:
        logger.error("Ошибка при обработке изображения: %s", e)
        raise


# Дополнительная функция для пакетной обработки множества изображений
async def batch_image_handler(
    files: list[bytes], directory: str, image_width: int
) -> list[Path]:
    """
    Asynchronously processes multiple images in parallel.

    Args:
        files (list[bytes]): A list of images in bytes.
        directory (str): A catalogue for saving images.
        image_width (int): The width of the image after resizing.

    Returns:
        list[Path]: A list of paths to saved images.
    """

    tasks = [image_handler(file, directory, image_width) for file in files]
    return await asyncio.gather(*tasks)


if __name__ == "__main__":
    image = bytes(open(input("Image path: "), "rb").read())
    width = 1000
    image_handler(image, "test", width)
