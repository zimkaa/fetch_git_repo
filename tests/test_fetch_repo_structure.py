import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientSession, web

from src.main import _fetch_repo_structure
from src.my_types import ResponseStructure
from tests.conftest import get_response_structure_dict


async def response(request):
    return web.json_response(get_response_structure_dict())


@pytest.fixture()
def session_repo_structure(event_loop, aiohttp_client):
    app = web.Application()
    app.router.add_get("/", response)
    return event_loop.run_until_complete(aiohttp_client(app))


@pytest.mark.asyncio()
async def test_fetch_repo_structure_success(
    session_repo_structure,
    response_structure_dict,
) -> None:
    session = session_repo_structure
    result = await _fetch_repo_structure("/", session)
    assert isinstance(result, ResponseStructure)
    assert result.sha == response_structure_dict["sha"]
    assert result.url == response_structure_dict["url"]
    assert len(result.tree) == len(response_structure_dict["tree"])
    assert not result.truncated


@pytest.mark.asyncio()
async def test_fetch_repo_structure_timeout_exception() -> None:
    with patch.object(
        ClientSession,
        "get",
        side_effect=asyncio.TimeoutError,
    ) as mock_get:
        async with ClientSession() as session:
            with pytest.raises(asyncio.TimeoutError):
                await _fetch_repo_structure("http://example.com", session)

            mock_get.assert_called()
