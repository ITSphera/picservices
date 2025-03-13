from io import BytesIO

from fastapi import HTTPException
from fastapi import status
from PIL import Image
from PIL import UnidentifiedImageError

from src.base import text_codes


async def validate_image(file_content: bytes) -> None:
    """
    Проверяет, является ли файл корректным изображением.
    Выбрасывает HTTPException, если изображение некорректно.
    """

    try:
        with Image.open(BytesIO(file_content)) as img:
            # Проверка наличия формата изображения
            if not img.format:
                raise ValueError(text_codes.UNKNOWN_IMAGE_FORMAT)
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=text_codes.FILE_NOT_IMAGE,
        )
    except Exception as e:
        # Можно добавить логирование ошибки здесь
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{text_codes.ERROR_IMAGE_HANDLER}: {str(e)}",
        )
