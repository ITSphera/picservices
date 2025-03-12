import io
from datetime import timedelta
from pathlib import Path
from shutil import rmtree
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient
from PIL import Image

from src.images.middlewares.limit_requests import LimitRequestsMiddleware
from src.main import app

# create media dir before tests
Path("src/media/tmp").mkdir(parents=True, exist_ok=True)


@pytest.fixture
def tmpdir():
    """

    :return:
    """

    return Path("src/media/tmp")


@pytest.fixture
def temp_test_dir(tmpdir):
    """
    Create test directory

    :param tmpdir:
    :return:
    """

    test_dir = Path(tmpdir) / "test_images"
    test_dir.mkdir(parents=True, exist_ok=True)
    return str(test_dir)


@pytest.fixture
def clean_test_catalog():
    """
    Clean all files in test catalog src/media/test
    :return:
    """

    temp_dir = Path("src/media/tmp/")
    yield
    for item in temp_dir.iterdir():
        if item.is_dir():
            rmtree(item)
        else:
            item.unlink()


@pytest_asyncio.fixture(scope="session")
async def async_client():
    """
    Fixture for async client
    :return:
    """

    async with AsyncClient(
        app=app, base_url="http://test"
    ) as async_test_client:
        yield async_test_client


@pytest.fixture(scope="session")
def create_test_image():
    """
    Create test image
    :return:
    """

    def _create_image(width=500, height=250, color=(255, 0, 0), format="PNG"):
        image = Image.new("RGB", (width, height), color)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()

    return _create_image


@pytest.fixture(scope="session")
def image(create_test_image):
    """
    Standard test image with size 500x250
    :param create_test_image:
    :return:
    """

    return create_test_image(500, 250, (255, 0, 0))


@pytest.fixture
def image_height_more_than_1080(create_test_image):
    """
    Standard test image with height more than 1080
    :param create_test_image:
    :return:
    """

    return create_test_image(500, 2000, (0, 255, 0))


@pytest.fixture
def wide_image(create_test_image):
    """
    Very wide image for testing BILINEAR resampling
    :param create_test_image:
    :return:
    """

    return create_test_image(5000, 2500, (0, 0, 255))


@pytest.fixture(scope="session")
def not_image():
    """
    Create not image
    :return:
    """

    return b"This is not an image file content"


@pytest.fixture
def corrupted_image(image):
    """
    Create corrupted image
    :return:
    """

    corrupted = bytearray(image)
    corrupted[20:25] = b"XXXXX"
    return bytes(corrupted)


@pytest.fixture
def empty_bytes():
    """
    Create empty bytes
    :return:
    """

    return b""


@pytest.fixture
def redis_mock():
    """
    Fixture for mock redis
    :return:
    """

    mock = AsyncMock()
    mock.exists = AsyncMock()
    mock.setex = AsyncMock()
    # Настраиваем мок для register_script
    mock.register_script.return_value = AsyncMock()
    return mock


@pytest.fixture
def middleware(app, redis_mock):
    """
    Fixture for middleware
    :return:
    """

    return LimitRequestsMiddleware(
        app=app,
        redis_server=redis_mock,
        max_requests=10,
        time_window=timedelta(minutes=1),
        blacklist_duration=timedelta(minutes=5),
        whitelist_paths=["/docs", "/health"],
        cache_control_header="max-age=5, public",
    )


@pytest.fixture
def mock_request():
    """
    Fixture for mock request
    :return:
    """

    request = MagicMock()
    request.client.host = "127.0.0.1"
    request.url.path = "/api/test"
    return request


@pytest.fixture
def mock_response():
    """
    Fixture for mock response
    :return:
    """

    response = MagicMock()
    response.headers = {}
    return response


@pytest.fixture
def call_next_mock(mock_response):
    """
    Fixture for mock call_next
    :param mock_response:
    :return:
    """

    async def _call_next(_):
        return mock_response

    return _call_next
