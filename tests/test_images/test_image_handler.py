import os

import pytest
from PIL import Image
from PIL import UnidentifiedImageError

from src.images.image_handler import batch_image_handler
from src.images.image_handler import image_handler


# Тесты для image_handler
@pytest.mark.asyncio
async def test_image_handler_normal(image, temp_test_dir):
    """
    Image handler test with standard image
    :param image:
    :param temp_test_dir:
    :return:
    """

    width = 1000
    new_image_path = await image_handler(image, temp_test_dir, width)

    assert new_image_path.exists()

    with Image.open(new_image_path) as img:
        assert img.width == width
        assert img.height == 500  # Должно сохранять пропорции
        assert img.format == "WEBP"


@pytest.mark.asyncio
async def test_image_handler_crop_tall_image(
    image_height_more_than_1080, temp_test_dir
):
    """
    Test image handler with tall image
    :param image_height_more_than_1080:
    :param temp_test_dir:
    :return:
    """

    width = 1000
    new_image_path = await image_handler(
        image_height_more_than_1080, temp_test_dir, width
    )

    assert new_image_path.exists()

    with Image.open(new_image_path) as img:
        assert img.width == width
        # Высота должна быть обрезана до MAX_IMAGE_HEIGHT
        assert img.height == 1080
        assert img.format == "WEBP"


@pytest.mark.asyncio
async def test_image_handler_wide_image(wide_image, temp_test_dir):
    """
    Test image handler with wide image
    :param wide_image:
    :param temp_test_dir:
    :return:
    """

    width = 1000
    new_image_path = await image_handler(wide_image, temp_test_dir, width)

    assert new_image_path.exists()

    with Image.open(new_image_path) as img:
        assert img.width == width
        assert img.height == 500  # 5000:2500 = 1000:500
        assert img.format == "WEBP"


@pytest.mark.asyncio
async def test_image_handler_small_resize(image, temp_test_dir):
    """
    Test image handler with small image
    :param image:
    :param temp_test_dir:
    :return:
    """

    width = 100  # Меньше оригинала
    new_image_path = await image_handler(image, temp_test_dir, width)

    assert new_image_path.exists()

    with Image.open(new_image_path) as img:
        assert img.width == width
        assert img.height == 50  # 500:250 = 100:50
        assert img.format == "WEBP"


@pytest.mark.asyncio
async def test_image_handler_large_resize(image, temp_test_dir):
    """
    Test image handler with large image
    :param image:
    :param temp_test_dir:
    :return:
    """

    width = 2000  # Больше оригинала
    new_image_path = await image_handler(image, temp_test_dir, width)

    assert new_image_path.exists()

    with Image.open(new_image_path) as img:
        assert img.width == width
        assert img.height == 1000  # 500:250 = 2000:1000
        assert img.format == "WEBP"


@pytest.mark.asyncio
async def test_image_handler_zero_width(image, temp_test_dir):
    """
    Test image handler with zero width
    :param image:
    :param temp_test_dir:
    :return:
    """

    width = 0
    with pytest.raises(ValueError):
        await image_handler(image, temp_test_dir, width)


@pytest.mark.asyncio
async def test_image_handler_negative_width(image, temp_test_dir):
    """
    Test image handler with negative width
    :param image:
    :param temp_test_dir:
    :return:
    """

    width = -100
    with pytest.raises(ValueError):
        await image_handler(image, temp_test_dir, width)


@pytest.mark.asyncio
async def test_not_image_handler(not_image, temp_test_dir):
    """
    Test image handler with not image
    :param not_image:
    :param temp_test_dir:
    :return:
    """

    width = 1000
    with pytest.raises(
        UnidentifiedImageError, match="cannot identify image file"
    ):
        await image_handler(not_image, temp_test_dir, width)


@pytest.mark.asyncio
async def test_corrupted_image_handler(corrupted_image, temp_test_dir):
    """
    Test image handler with corrupted image
    :param corrupted_image:
    :param temp_test_dir:
    :return:
    """

    width = 1000
    with pytest.raises((UnidentifiedImageError, OSError)):
        await image_handler(corrupted_image, temp_test_dir, width)


@pytest.mark.asyncio
async def test_empty_bytes_handler(empty_bytes, temp_test_dir):
    """
    Test image handler with empty bytes
    :param empty_bytes:
    :param temp_test_dir:
    :return:
    """

    width = 1000
    with pytest.raises((UnidentifiedImageError, ValueError)):
        await image_handler(empty_bytes, temp_test_dir, width)


@pytest.mark.asyncio
async def test_directory_creation(image, tmpdir):
    """
    Test directory creation
    :param image:
    :param tmpdir:
    :return:
    """

    width = 1000
    non_existent_dir = "non_existent_subdir"
    full_path = os.path.join(tmpdir, non_existent_dir)

    # Проверяем, что директория ещё не существует
    assert not os.path.exists(full_path)

    # Исправляем передачу пути директории
    new_image_path = await image_handler(image, non_existent_dir, width)

    # Проверяем, что файл был создан
    assert os.path.exists(new_image_path)

    # Проверяем, что директория была создана (используем родительскую директорию файла)
    assert os.path.exists(os.path.dirname(new_image_path))


# Тесты для batch_image_handler


@pytest.mark.asyncio
async def test_batch_image_handler(create_test_image, temp_test_dir):
    """
    Test batch image handler
    :param create_test_image:
    :param temp_test_dir:
    :return:
    """

    # Создаём несколько тестовых изображений
    images = [
        create_test_image(400, 300, (255, 0, 0)),
        create_test_image(500, 400, (0, 255, 0)),
        create_test_image(600, 500, (0, 0, 255)),
    ]

    width = 800
    paths = await batch_image_handler(images, temp_test_dir, width)

    # Проверяем, что все изображения были обработаны
    assert len(paths) == 3

    for i, path in enumerate(paths):
        assert path.exists()

        with Image.open(path) as img:
            assert img.width == width
            # Высоты должны соответствовать пропорциям
            expected_heights = [
                600,
                640,
                667,
            ]  # Примерные значения с округлением
            assert (
                abs(img.height - expected_heights[i]) <= 1
            )  # Допускаем погрешность в 1 пиксель из-за округления
            assert img.format == "WEBP"


@pytest.mark.asyncio
async def test_batch_empty_list(temp_test_dir):
    """
    Test batch image handler with empty list
    :param temp_test_dir:
    :return:
    """

    width = 800
    paths = await batch_image_handler([], temp_test_dir, width)

    assert len(paths) == 0


@pytest.mark.asyncio
async def test_batch_with_invalid_images(
    create_test_image, not_image, temp_test_dir
):
    """
    Test batch image handler with invalid images
    :param create_test_image:
    :param not_image:
    :param temp_test_dir:
    :return:
    """

    images = [
        create_test_image(400, 300),
        not_image,
        create_test_image(600, 500),
    ]

    width = 800

    # Должно вызвать исключение из-за некорректного изображения во втором элементе
    with pytest.raises(UnidentifiedImageError):
        await batch_image_handler(images, temp_test_dir, width)
