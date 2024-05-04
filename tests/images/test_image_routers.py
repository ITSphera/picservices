import pytest
from asyncio import sleep


@pytest.mark.asyncio
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
    assert response.json()["message"] == "Image processing started"


@pytest.mark.asyncio
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
    assert response.json()["error"] == "Service 'wrong_service' not found"


@pytest.mark.asyncio
async def test_upload_image_with_wrong_target_type(async_client, image):
    """
    Test upload image with wrong target type
    :param async_client:
    :param image:
    :return:
    """

    file = {"file": image}
    upload_data = {
        "service": "SVZ",
        "target_type": "wrong_target_type",
    }
    response = await async_client.post(
        "images/upload", files=file, params=upload_data
    )

    assert response.status_code == 422
    assert (
        response.json()["error"]
        == "Target type 'wrong_target_type' not found for service 'SVZ'"
    )


@pytest.mark.asyncio
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

    assert response.status_code == 422
    assert (
        response.json()["error"]
        == "Error processing image: File is not an image"
    )


@pytest.mark.asyncio
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
    assert response.json()["message"] == "Image processing started"

    task_id = response.json()["task_id"]

    await sleep(3)

    response = await async_client.get(f"images/status/{task_id}")

    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "SUCCESS"
    assert response.json()["result"].startswith("http")
