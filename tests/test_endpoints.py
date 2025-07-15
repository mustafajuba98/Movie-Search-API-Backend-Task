# tests/test_endpoints.py

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from app.main import app

@pytest.fixture(autouse=True)
async def init_cache():
    """
    Fixture to initialize and shut down the cache for each test session.
    'autouse=True' means it runs automatically for every test.
    """
    FastAPICache.init(InMemoryBackend(), prefix="pytest-cache")
    yield
    FastAPICache.reset()


@pytest.mark.asyncio
async def test_read_root():
    """
    Test that the root endpoint returns a 200 OK status and the correct message.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to the Movie Search API! Navigate to /docs for API documentation."}


@pytest.mark.asyncio
async def test_search_movies_success():
    """
    Test a successful movie search by title.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/movies/search?title=Matrix")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["response"] is True
    assert "search_results" in response_data


@pytest.mark.asyncio
async def test_search_movies_requires_parameter():
    """
    Test that the search endpoint returns a 400 Bad Request error
    if no search parameters are provided.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/movies/search")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "must be provided" in response.json()["detail"]