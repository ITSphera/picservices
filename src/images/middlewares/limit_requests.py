from datetime import timedelta
from typing import Any

from fastapi import Request, FastAPI
from redis import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class LimitRequestsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for limiting requests per IP address.
    """

    def __init__(
        self,
        app: FastAPI,
        redis_server: Redis,
        max_requests: int,
        time_window: timedelta,
        blacklist_duration: timedelta,
    ):
        super().__init__(app)
        self.redis = redis_server
        self.max_requests = max_requests
        self.time_window = time_window
        self.blacklist_duration = blacklist_duration

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        """
        Dispatch the request.
        :param request: Request object
        :param call_next: Callable
        :return: Response
        """
        client_ip: str = request.client.host

        if await self.is_blacklisted(client_ip):
            return JSONResponse(status_code=429, content="Too many requests")

        request_count: int = await self.get_request_count(client_ip)

        if request_count >= self.max_requests:
            await self.add_to_blacklist(client_ip)
            return JSONResponse(status_code=429, content="Too many requests")

        await self.increment_request_count(client_ip)

        response: Any = await call_next(request)
        return response

    async def is_blacklisted(self, client_ip: str) -> bool:
        """
        Check if the IP is blacklisted.
        :param client_ip: IP address
        :return: boolean value
        """

        return self.redis.exists(f"blacklist:{client_ip}")

    async def add_to_blacklist(self, client_ip: str) -> None:
        """
        Add the IP address to the blacklist.
        :param client_ip: IP address
        :return: None
        """

        self.redis.setex(
            f"blacklist:{client_ip}",
            int(self.blacklist_duration.total_seconds()),
            1,
        )

    async def get_request_count(self, client_ip: str) -> int:
        """
        Get the number of requests for the IP address.
        :param client_ip: IP address
        :return: integer value
        """

        request_count: str = self.redis.get(f"request_count:{client_ip}")
        return int(request_count) if request_count else 0

    async def increment_request_count(self, client_ip: str) -> None:
        """
        Increment the number of requests for the IP address.
        :param client_ip: IP address
        :return: None
        """

        pipeline: Redis.pipeline = self.redis.pipeline()
        pipeline.incr(f"request_count:{client_ip}")
        pipeline.expire(
            f"request_count:{client_ip}", int(self.time_window.total_seconds())
        )
        pipeline.execute()
