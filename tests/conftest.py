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
Path("src/media/test").mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def clean_test_catalog():
    """
    Clean all files in test catalog src/media/test
    :return:
    """

    temp_dir = Path("src/media/test/")
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


@pytest.fixture(scope="module")
def image():
    """
    Create test image
    :return:
    """

    image = Image.new("RGB", (100, 50))
    image.save("src/media/test/test.png")
    image = bytes(open("src/media/test/test.png", "rb").read())
    yield image


@pytest.fixture(scope="session")
def not_image():
    """
    Create not image
    :return:
    """

    with open("src/media/test/test.txt", "w+") as my_file:
        my_file.write("Привет, файл!")
    not_image = bytes(open("src/media/test/test.txt", "rb").read())
    yield not_image


@pytest.fixture(scope="session")
def image_height_more_than_1080():
    """
    Create test image with height more than 1080
    :return:
    """

    image = Image.new("RGB", (100, 2000))
    image.save("src/media/test/test2000.png")
    image = bytes(open("src/media/test/test2000.png", "rb").read())
    yield image


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
