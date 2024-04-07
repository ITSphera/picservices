import pytest
from PIL import Image, UnidentifiedImageError

from src.images.image_handler import image_handler


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
