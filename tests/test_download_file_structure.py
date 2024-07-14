from unittest.mock import AsyncMock

import pytest
from aiohttp import web

from tests.conftest import get_file_dict
from tests.conftest import tree_element_blob
from src.main import _download_file_structure


async def response(request):
    return web.json_response(get_file_dict())


@pytest.fixture()
def session_download(event_loop, aiohttp_client):
    app = web.Application()
    app.router.add_get("/git/blobs/b9c199c98f9bec183a195a9c0afc0a2e4fcc7654", response)
    return event_loop.run_until_complete(aiohttp_client(app))


@pytest.mark.asyncio()
async def test_download_file_structure_success(session_download, file_structure) -> None:
    session = session_download
    elements = (tree_element_blob,)
    result = await _download_file_structure(elements, session)

    expected = [file_structure]
    assert result == expected


@pytest.mark.asyncio()
async def test_download_file_structure_empty_elements() -> None:
    mock_session = AsyncMock()

    result = await _download_file_structure((), mock_session)

    assert result == []
