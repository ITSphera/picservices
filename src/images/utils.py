from functools import lru_cache
from pathlib import Path
from urllib.parse import urljoin

from src.config import BASE_URL


@lru_cache(maxsize=100)
def get_file_url(file_path: str) -> str:
    """
    Get the URL of the cached file

    Args:
        file_path (str): File path

    Returns:
        str: URL file
    """

    try:
        # Получаем путь относительно каталога src/media
        rel_path = Path(file_path).relative_to("src/media")
        print(f"rel_path: {rel_path}")
    except ValueError as e:
        raise ValueError(
            f"Файл '{file_path}' не находится в каталоге 'src/media'."
        ) from e

        # Формируем URL с помощью urljoin, чтобы корректно обрабатывать слэши
    return urljoin(BASE_URL.rstrip("/") + "/", f"media/{rel_path}")
