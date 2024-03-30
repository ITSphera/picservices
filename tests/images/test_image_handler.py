import os
import shutil

import pytest
from PIL import Image, UnidentifiedImageError

from src.images.image_handler import image_handler


@pytest.fixture(scope="session")
def image():
    image = Image.new("RGB", (100, 50))
    image.save("test.png")
    image = bytes(open("test.png", "rb").read())
    yield image
    os.remove("test.png")


@pytest.fixture(scope="session")
def not_image():
    with open("test.txt", "w+") as my_file:
        my_file.write("Привет, файл!")
    not_image = bytes(open("test.txt", "rb").read())
    yield not_image
    os.remove("test.txt")


@pytest.fixture(scope="session")
def image_height_more_than_1080():
    image = Image.new("RGB", (100, 2000))
    image.save("test2000.png")
    image = bytes(open("test2000.png", "rb").read())
    yield image
    os.remove("test2000.png")


def test_image_handler(image):
    """
    Test image handler with create test image
    :return:
    """

    width = 1000
    new_image = image_handler(image, "test", width)

    assert new_image

    image = Image.open(new_image)

    assert image.width == width
    assert image.height == 500
    assert image.format == "WEBP"

    shutil.rmtree("src/media/test")


def test_not_image_handler(not_image):
    """
    Test image handler with not image
    :return:
    """

    width = 1000
    with pytest.raises(
        UnidentifiedImageError, match="cannot identify image file"
    ):
        image_handler(not_image, "test", width)


def test_image_height_more_than_1080(image_height_more_than_1080):
    """
    Test image handler with create test image
    :return:
    """

    width = 1000
    new_image = image_handler(image_height_more_than_1080, "test", width)

    assert new_image

    image = Image.open(new_image)

    assert image.width == width
    assert image.height == 1080
    assert image.format == "WEBP"

    shutil.rmtree("src/media/test")
