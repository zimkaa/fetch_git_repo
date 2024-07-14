from unittest.mock import patch

import pytest
from aiohttp import web

from tests.conftest import get_response_structure_dict
from src.main import main


URL = "/"


async def response_structure(request):
    return web.json_response(get_response_structure_dict())


@pytest.fixture()
def session(event_loop, aiohttp_client):
    app = web.Application()
    app.router.add_get("/", response_structure)
    return event_loop.run_until_complete(aiohttp_client(app))


@pytest.mark.asyncio()
async def test_main_error_handling(get_response_structure, file_structure) -> None:
    with patch("src.main.ClientSession") as MockClientSession, patch(
        "src.main._fetch_repo_structure",
    ) as mock_fetch_repo_structure, patch(
        "src.main._download_file_structure",
    ) as mock_download_file_structure, patch(
        "src.main._write_file",
    ) as mock_write_file, patch("src.main._calculate_hash") as mock_calculate_hash:
        mock_fetch_repo_structure.return_value = get_response_structure
        mock_download_file_structure.return_value = [file_structure]

        await main()

        MockClientSession.assert_called()
        mock_fetch_repo_structure.assert_called()
        mock_download_file_structure.assert_called()
        mock_write_file.assert_called()
        mock_calculate_hash.assert_called()
