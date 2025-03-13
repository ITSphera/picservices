from asyncio import sleep

from src.base import text_codes


async def test_upload_image(async_client, image):
    """
    Test upload image

    :param async_client:
    :param image:
    :return:
    """

    file = {"file": image}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )

    assert response.status_code == 200
    response_json = response.json()
    assert "task_id" in response_json
    assert response.json()["message"] == text_codes.IMAGE_PROCESSING_STARTED


async def test_upload_image_with_wrong_service(async_client, image):
    """
    Test upload image with wrong service
    :param async_client:
    :param image:
    :return:
    """

    file = {"file": image}
    upload_data = {
        "service": "wrong_service",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )

    assert response.status_code == 422
    print(response.json())
    error_detail = response.json()["detail"][0]
    assert "Service 'wrong_service' not found" in error_detail["msg"]


async def test_upload_image_with_wrong_target_type(async_client, image):
    """
    Test upload image with wrong target type
    :param async_client:
    :param image:
    :return:
    """

    file = {"file": image}
    upload_data = {
        "service": "svz",
        "target_type": "wrong_target_type",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )

    assert response.status_code == 422
    error_detail = response.json()["detail"][0]
    assert "Target type 'wrong_target_type' not found" in error_detail["msg"]


async def test_upload_image_with_wrong_image(async_client, not_image):
    """
    Test upload image with wrong image
    :param async_client:
    :param not_image:
    :return:
    """

    file = {"file": not_image}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )

    assert response.status_code == 400
    assert response.json()["error"] == "The file is not an image."


async def test_upload_image_min_size(async_client, image_width_small):
    """
    Test upload image min size
    :param async_client:
    :param image_width_small:
    :return:
    """

    file = {"file": image_width_small}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == text_codes.IMAGE_PROCESSING_STARTED


async def test_upload_image_large_height(
    async_client, image_height_more_than_1080
):
    """
    Test upload image large height
    :param async_client:
    :param image_height_more_than_1080:
    :return:
    """

    file = {"file": image_height_more_than_1080}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == text_codes.IMAGE_PROCESSING_STARTED


async def test_upload_wide_image(async_client, wide_image):
    """
    Test upload wide image
    :param async_client:
    :param wide_image:
    :return:
    """

    file = {"file": wide_image}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )
    assert response.status_code == 200
    assert response.json()["message"] == text_codes.IMAGE_PROCESSING_STARTED


async def test_upload_not_image(async_client, not_image):
    """
    Test upload not image
    :param async_client:
    :param not_image:
    :return:
    """

    file = {"file": not_image}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )
    assert response.status_code == 400
    assert response.json()["error"] == text_codes.FILE_NOT_IMAGE


async def test_upload_corrupted_image(async_client, corrupted_image):
    """
    Test upload corrupted image
    :param async_client:
    :param corrupted_image:
    :return:
    """

    file = {"file": corrupted_image}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )
    assert response.status_code == 400
    assert response.json()["error"] == text_codes.FILE_NOT_IMAGE


async def test_upload_empty_file(async_client, empty_bytes):
    """
    Test upload empty file
    :param async_client:
    :param empty_bytes:
    :return:
    """

    file = {"file": empty_bytes}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )
    assert response.status_code == 400
    assert response.json()["error"] == text_codes.FILE_NOT_IMAGE


async def test_get_status(async_client, image):
    """
    Test get status
    :param async_client:
    :param image:
    :return:
    """

    file = {"file": image}
    upload_data = {
        "service": "test",
        "target_type": "test",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Image processing started."

    task_id = response.json()["task_id"]

    await sleep(1)

    response = await async_client.get(f"images/status/{task_id}")

    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "SUCCESS"
    assert response.json()["result"].startswith("http")


async def test_get_status_pending(async_client, mocker):
    """
    Test get status pending
    :param async_client:
    :param mocker:
    :return:
    """

    task_id = "test_task_id"
    mock_task = mocker.patch("celery.result.AsyncResult")
    mock_task.state = "PENDING"

    response = await async_client.get(f"images/status/{task_id}")

    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "PENDING"
    assert response.json()["result"] is None
