from datetime import timedelta
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi import status
from starlette.responses import JSONResponse

from src.images.middlewares.limit_requests import LimitRequestsMiddleware

pytestmark = pytest.mark.asyncio


@pytest.fixture
def app():
    """
    Fixture for app
    :return:
    """
    return FastAPI()


# Тесты для should_process_request
def test_should_process_request_normal_path(middleware, mock_request):
    """
    Test normal path

    :param middleware:
    :param mock_request:
    :return:
    """

    assert middleware.should_process_request(mock_request) is True


def test_should_process_request_whitelist_path(middleware, mock_request):
    """
    Test whitelisted path
    :param middleware:
    :param mock_request:
    :return:
    """

    mock_request.url.path = "/docs"
    assert middleware.should_process_request(mock_request) is False


def test_should_process_request_whitelist_subpath(middleware, mock_request):
    """
    Test whitelisted subpath
    :param middleware:
    :param mock_request:
    :return:
    """

    mock_request.url.path = "/docs/swagger"
    assert middleware.should_process_request(mock_request) is False


# Тесты для _get_keys
def test_get_keys_format(middleware):
    """
    Test keys format
    :param middleware:
    :return:
    """

    client_ip = "192.168.1.1"
    blacklist_key, counter_key = middleware._get_keys(client_ip)

    assert blacklist_key == "ratelimit:bl:192.168.1.1"
    assert counter_key == "ratelimit:req:192.168.1.1"


def test_get_keys_custom_prefix(app, redis_mock):
    """
    Test custom prefix
    :param app:
    :param redis_mock:
    :return:
    """

    custom_middleware = LimitRequestsMiddleware(
        app=app,
        redis_server=redis_mock,
        max_requests=10,
        time_window=timedelta(minutes=1),
        blacklist_duration=timedelta(minutes=5),
        redis_key_prefix="custom:",
    )

    client_ip = "192.168.1.1"
    blacklist_key, counter_key = custom_middleware._get_keys(client_ip)

    assert blacklist_key == "custom:bl:192.168.1.1"
    assert counter_key == "custom:req:192.168.1.1"


# Тесты для check_limits
async def test_check_limits_ip_not_blacklisted(middleware, redis_mock):
    """
    Test IP not blacklisted
    :param middleware:
    :param redis_mock:
    :return:
    """

    client_ip = "127.0.0.1"

    # Настройка моков
    redis_mock.exists.return_value = False
    middleware.increment_script = AsyncMock(
        return_value=5
    )  # Счетчик меньше лимита

    allowed, count = await middleware.check_limits(client_ip)

    assert allowed is True
    assert count == 5
    # Проверяем, что был вызван метод exists с правильным ключом
    redis_mock.exists.assert_called_once_with(
        f"{middleware.prefix}bl:{client_ip}"
    )
    # Проверяем, что был вызван increment_script с правильными аргументами
    middleware.increment_script.assert_called_once()


async def test_check_limits_ip_blacklisted(middleware, redis_mock):
    """
    Test IP blacklisted
    :param middleware:
    :param redis_mock:
    :return:
    """

    client_ip = "127.0.0.1"

    # Настройка моков
    redis_mock.exists.return_value = True

    # Переопределяем increment_script на AsyncMock, чтобы можно было проверить его вызовы
    middleware.increment_script = AsyncMock()

    allowed, count = await middleware.check_limits(client_ip)

    assert allowed is False
    assert count is None
    # Проверяем, что был вызван метод exists с правильным ключом
    redis_mock.exists.assert_called_once_with(
        f"{middleware.prefix}bl:{client_ip}"
    )
    # Проверяем, что increment_script не был вызван
    middleware.increment_script.assert_not_called()


async def test_check_limits_exceeds_max_requests(middleware, redis_mock):
    """
    Test IP exceeds max requests
    :param middleware:
    :param redis_mock:
    :return:
    """

    client_ip = "127.0.0.1"

    # Настройка моков
    redis_mock.exists.return_value = False
    middleware.increment_script = AsyncMock(
        return_value=11
    )  # Счетчик больше лимита

    allowed, count = await middleware.check_limits(client_ip)

    assert allowed is False
    assert count == 11
    # Проверяем, что IP был добавлен в черный список
    redis_mock.setex.assert_called_once_with(
        f"{middleware.prefix}bl:{client_ip}",
        middleware.blacklist_duration_seconds,
        1,
    )


async def test_check_limits_redis_exception(middleware, redis_mock):
    """
    Test Redis exception
    :param middleware:
    :param redis_mock:
    :return:
    """

    client_ip = "127.0.0.1"

    # Настройка моков для имитации отсутствия записи в blacklist
    redis_mock.exists.return_value = False

    # Замена increment_script на AsyncMock с side_effect для генерации исключения
    middleware.increment_script = AsyncMock(
        side_effect=redis.RedisError("Connection error")
    )

    allowed, count = await middleware.check_limits(client_ip)

    # В случае ошибки Redis, middleware должен пропустить запрос (allowed=True, count=None)
    assert allowed is True
    assert count is None


# Тесты для dispatch
async def test_dispatch_whitelist_path(
    middleware, mock_request, call_next_mock, mock_response
):
    """
    Test whitelisted path
    :param middleware:
    :param mock_request:
    :param call_next_mock:
    :param mock_response:
    :return:
    """

    mock_request.url.path = "/docs"

    response = await middleware.dispatch(mock_request, call_next_mock)

    middleware.increment_script = AsyncMock()

    # Должен вернуть ответ без проверки ограничений
    assert response == mock_response
    # Проверяем, что лимиты не проверялись
    middleware.increment_script.assert_not_called()


async def test_dispatch_allowed_request(
    middleware, mock_request, call_next_mock, mock_response, monkeypatch
):
    """
    Test dispatch for allowed request
    :param middleware:
    :param mock_request:
    :param call_next_mock:
    :param mock_response:
    :param monkeypatch:
    :return:
    """

    # Используем monkeypatch для замены check_limits
    async def mock_check_limits(client_ip):
        return True, 5

    monkeypatch.setattr(middleware, "check_limits", mock_check_limits)

    response = await middleware.dispatch(mock_request, call_next_mock)

    # Должен вернуть ответ с заголовками о лимитах
    assert response == mock_response
    assert response.headers["Cache-Control"] == "max-age=5, public"
    assert response.headers["X-RateLimit-Limit"] == "10"
    assert response.headers["X-RateLimit-Remaining"] == "5"
    assert response.headers["X-RateLimit-Reset"] == "60"


async def test_dispatch_blocked_request(
    middleware, mock_request, call_next_mock, monkeypatch
):
    """
    Test dispatch for blocked request
    :param middleware:
    :param mock_request:
    :param call_next_mock:
    :param monkeypatch:
    :return:
    """

    # Используем monkeypatch для замены check_limits
    async def mock_check_limits(client_ip):
        return False, 11

    monkeypatch.setattr(middleware, "check_limits", mock_check_limits)

    response = await middleware.dispatch(mock_request, call_next_mock)

    # Должен вернуть JSONResponse с кодом 429
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "error" in response.body.decode()
    assert "retry_after" in response.body.decode()
    assert response.headers["Retry-After"] == "300"


async def test_dispatch_check_limits_exception(
    middleware, mock_request, call_next_mock, mock_response, monkeypatch
):
    """
    Test dispatch for check_limits exception
    :param middleware:
    :param mock_request:
    :param call_next_mock:
    :param mock_response:
    :param monkeypatch:
    :return:
    """

    # Используем monkeypatch для замены check_limits, чтобы вызвать исключение
    async def mock_check_limits(client_ip):
        raise Exception("Test exception")

    monkeypatch.setattr(middleware, "check_limits", mock_check_limits)

    response = await middleware.dispatch(mock_request, call_next_mock)

    # Должен продолжить обработку запроса даже при ошибке
    assert response == mock_response


async def test_dispatch_response_headers_exception(
    middleware, mock_request, call_next_mock, monkeypatch
):
    """
    Test dispatch for response headers exception
    :param middleware:
    :param mock_request:
    :param call_next_mock:
    :param monkeypatch:
    :return:
    """

    # Используем monkeypatch для замены check_limits
    async def mock_check_limits(client_ip):
        return True, 5

    monkeypatch.setattr(middleware, "check_limits", mock_check_limits)

    # Создаем ответ, который вызовет ошибку при добавлении заголовков
    async def _call_next_error(_):
        response = MagicMock()
        response.headers = MagicMock()
        response.headers.__setitem__.side_effect = Exception("Headers error")
        return response

    response = await middleware.dispatch(mock_request, _call_next_error)

    # Должен вернуть ответ даже при ошибке в заголовках
    assert response is not None


# Тест интеграции компонентов
async def test_middleware_full_workflow(
    middleware, mock_request, call_next_mock, mock_response, redis_mock
):
    """
    Test middleware full workflow
    :param middleware:
    :param mock_request:
    :param call_next_mock:
    :param mock_response:
    :param redis_mock:
    :return:
    """

    # Настройка моков
    redis_mock.exists.return_value = False
    middleware.increment_script = AsyncMock(return_value=5)

    response = await middleware.dispatch(mock_request, call_next_mock)

    # Проверяем конечный результат
    assert response == mock_response
    assert "X-RateLimit-Limit" in response.headers
    assert response.headers["X-RateLimit-Limit"] == "10"
    assert response.headers["X-RateLimit-Remaining"] == "5"
