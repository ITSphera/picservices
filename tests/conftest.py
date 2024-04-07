import pytest_asyncio
from httpx import AsyncClient

from main import app


@pytest_asyncio.fixture(scope="session")
async def async_client():
    """Fixture to create a FastAPI test client."""

    async with AsyncClient(
        app=app, base_url="http://test"
    ) as async_test_client:
        yield async_test_client
