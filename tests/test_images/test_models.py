import pytest
from pydantic import ValidationError

from src.images.models import UploadData


def test_valid_upload_data():
    """
    Testing for valid input data.
    It is expected that if service and target_type are valid, the model instance is created successfully,
    and get_target_info method returns correct data.
    :return:
    """

    data = {"service": "svz", "target_type": "avatar"}
    upload_data = UploadData(**data)
    target_info = upload_data.target_info
    expected_info = {"dir": "svz/avatars", "width": 200}
    assert target_info == expected_info


def test_invalid_service():
    """
    Тестирование случая, когда указан несуществующий сервис.
    Ожидается, что будет выброшено исключение ValueError с корректным сообщением.
    """

    data = {"service": "nonexistent", "target_type": "avatar"}
    with pytest.raises(ValueError, match="Service 'nonexistent' not found"):
        UploadData(**data)


def test_invalid_target_type():
    """
    Тестирование случая, когда для валидного сервиса указан несуществующий target_type.
    Ожидается, что будет выброшено исключение ValueError с корректным сообщением.
    """
    data = {"service": "svz", "target_type": "nonexistent"}
    with pytest.raises(
        ValueError,
        match="Target type 'nonexistent' not found for service 'svz'",
    ):
        UploadData(**data)


def test_missing_service():
    """
    Тестирование отсутствия обязательного поля 'service'.
    Ожидается, что будет выброшено исключение ValidationError.
    """
    data = {"target_type": "avatar"}
    with pytest.raises(ValidationError):
        UploadData(**data)


def test_missing_target_type():
    """
    Тестирование отсутствия обязательного поля 'target_type'.
    Ожидается, что будет выброшено исключение ValidationError.
    """
    data = {"service": "svz"}
    with pytest.raises(ValidationError):
        UploadData(**data)


def test_wrong_field_types():
    """
    Тестирование неверных типов входных данных.
    Ожидается, что будет выброшено исключение ValidationError, если поля не являются строками.
    """
    data = {"service": 123, "target_type": 456}
    with pytest.raises(ValidationError):
        UploadData(**data)
