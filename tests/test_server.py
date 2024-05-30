from typing import AsyncIterator

import httpx
import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as httpx_client:
        yield httpx_client


@pytest.mark.asyncio
async def test_get_request(client: httpx.AsyncClient) -> None:
    response = await client.get("http://127.0.0.1:8000")
    assert response.status_code == httpx.codes.OK


@pytest.mark.asyncio
async def test_post_request(client: httpx.AsyncClient) -> None:
    response = await client.post("http://127.0.0.1:8000", json={"data": "data"})
    assert response.status_code == httpx.codes.OK
    assert response.json() == {"data": "data"}
