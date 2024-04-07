import os

import pytest
import pytest_asyncio
from PIL import Image
from httpx import AsyncClient

from main import app


@pytest_asyncio.fixture(scope="session")
async def async_client():
    """Fixture to create a FastAPI test client."""

    async with AsyncClient(
        app=app, base_url="http://test"
    ) as async_test_client:
        yield async_test_client


@pytest.fixture(scope="session")
def image():
    """
    Create test image
    :return:
    """
    image = Image.new("RGB", (100, 50))
    image.save("test.png")
    image = bytes(open("test.png", "rb").read())
    yield image
    os.remove("test.png")


@pytest.fixture(scope="session")
def not_image():
    """
    Create not image
    :return:
    """
    with open("test.txt", "w+") as my_file:
        my_file.write("Привет, файл!")
    not_image = bytes(open("test.txt", "rb").read())
    yield not_image
    os.remove("test.txt")


@pytest.fixture(scope="session")
def image_height_more_than_1080():
    """
    Create test image with height more than 1080
    :return:
    """
    image = Image.new("RGB", (100, 2000))
    image.save("test2000.png")
    image = bytes(open("test2000.png", "rb").read())
    yield image
    os.remove("test2000.png")
