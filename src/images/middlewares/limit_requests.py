import logging
from datetime import timedelta
from typing import List
from typing import Optional
from typing import Tuple

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class LimitRequestsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting

    Args:
        app (FastAPI): FastAPI-application.
        redis_server (redis.Redis): Redis-server.
        max_requests (int): Maximum number of requests per time window.
        time_window (timedelta): Time window for rate limiting.
        blacklist_duration (timedelta): Duration of IP blacklist.
        redis_key_prefix (str, optional): Prefix for Redis keys. Defaults to "ratelimit:".
        whitelist_paths (List[str], optional): List of paths to exclude from rate limiting. Defaults to None.
        cache_control_header (str, optional): Cache-Control header value. Defaults to "max-age=5, public".
    """

    def __init__(
        self,
        app: FastAPI,
        redis_server: redis.Redis,
        max_requests: int,
        time_window: timedelta,
        blacklist_duration: timedelta,
        redis_key_prefix: str = "ratelimit:",
        whitelist_paths: List[str] = None,
        cache_control_header: str = "max-age=5, public",
    ):
        super().__init__(app)
        self.redis = redis_server
        self.max_requests = max_requests
        self.time_window_seconds = int(time_window.total_seconds())
        self.blacklist_duration_seconds = int(
            blacklist_duration.total_seconds()
        )
        self.prefix = redis_key_prefix
        self.whitelist_paths = whitelist_paths or []
        self.cache_control_header = cache_control_header

        # Lua-script for incrementing request counter
        self.lua_script = """
        local current = redis.call('incr', KEYS[1])
        if current == 1 then
            redis.call('expire', KEYS[1], ARGV[1])
        end
        return current
        """

        self.increment_script = self.redis.register_script(self.lua_script)

    def _get_keys(self, client_ip: str) -> Tuple[str, str]:
        """
        Generates keys for Redis

        Args:
            client_ip (str): The IP address of the client.

        Returns:
            Tuple[str, str]: A tuple containing the blacklist key and request counter key.
        """

        return (
            f"{self.prefix}bl:{client_ip}",  # blacklist key
            f"{self.prefix}req:{client_ip}",  # request counter key
        )

    def should_process_request(self, request: Request) -> bool:
        """
        Checks if the request should be processed

        Args:
            request (Request): The request object.

        Returns:
            bool: True if the request should be processed, False otherwise.
        """

        path = request.url.path
        return not any(
            path.startswith(wpath) for wpath in self.whitelist_paths
        )

    async def check_limits(self, client_ip: str) -> Tuple[bool, Optional[int]]:
        """
        Checks if the client has exceeded the rate limit

        Args:
            client_ip (str): The IP address of the client.

        Returns:
            Tuple[bool, Optional[int]]: A tuple containing a boolean indicating whether the client has exceeded the rate limit and the current request count.
        """

        blacklist_key, counter_key = self._get_keys(client_ip)
        try:
            is_blacklisted = await self.redis.exists(blacklist_key)
        except Exception as e:
            logger.error(
                "Error checking blacklist key %s: %s", blacklist_key, e
            )
            return True, None

        if is_blacklisted:
            return False, None

        try:
            current_count = await self.increment_script(
                keys=[counter_key], args=[self.time_window_seconds]
            )

            if int(current_count) > self.max_requests:
                await self.redis.setex(
                    blacklist_key, self.blacklist_duration_seconds, 1
                )
                return False, current_count

            return True, current_count
        except Exception as e:
            logging.exception(
                f"Error checking rate limit for {client_ip}: {e}"
            )
            return True, None

    async def get_client_ip(self, request: Request) -> str:
        """
        Returns the IP address of the client

        Args:
            request (Request): The request object.

        Returns:
            str: The IP address of the client.
        """

        forwarded = request.headers.get("X-Forwarded-For")
        return forwarded.split(",")[0] if forwarded else request.client.host

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        """
        Dispatches the request to the next middleware

        Args:
            request (Request): The request object.
            call_next: The next middleware function.

        Returns:
            JSONResponse: The response object.
        """

        if not self.should_process_request(request):
            return await call_next(request)

        client_ip = await self.get_client_ip(request)

        try:
            allowed, count = await self.check_limits(client_ip)

            if not allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too many requests",
                        "retry_after": self.blacklist_duration_seconds,
                    },
                    headers={
                        "Retry-After": str(self.blacklist_duration_seconds)
                    },
                )
        except Exception as e:
            # В случае любых ошибок в проверке лимитов просто продолжаем обработку запроса
            # Это предотвращает падение сервиса из-за проблем с middleware
            logging.exception(
                f"Error checking rate limit for {client_ip}: {e}"
            )

        response = await call_next(request)

        # Добавляем заголовки для кэширования на стороне клиента только если это возможно
        try:
            if self.cache_control_header and hasattr(response, "headers"):
                response.headers["Cache-Control"] = self.cache_control_header
                if count is not None:
                    response.headers["X-RateLimit-Limit"] = str(
                        self.max_requests
                    )
                    response.headers["X-RateLimit-Remaining"] = str(
                        max(0, self.max_requests - int(count))
                    )
                    response.headers["X-RateLimit-Reset"] = str(
                        self.time_window_seconds
                    )
        except Exception as e:
            logger.warning("Error setting rate limit headers: %s", e)

        return response
