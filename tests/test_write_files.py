from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from tests.conftest import ORIGINAL_STRING
from src.main import TEMP_PROJECT_FOLDER
from src.main import _write_files
from src.my_types import FileStructure


@pytest.mark.asyncio()
async def test_write_files_empty_list() -> None:
    with patch("aiofiles.open", MagicMock()) as mock_open:
        await _write_files([])
        mock_open.assert_not_called()


@pytest.mark.asyncio()
async def test_write_files_single_file(file_structure: FileStructure) -> None:
    with patch("aiofiles.open", MagicMock()) as mock_open:
        mock_file = AsyncMock()
        mock_open.return_value.__aenter__.return_value = mock_file
        await _write_files([file_structure])
        mock_open.assert_called_once_with(TEMP_PROJECT_FOLDER / file_structure.path, "w")
        mock_file.write.assert_called_once_with(ORIGINAL_STRING)


@pytest.mark.asyncio()
async def test_write_files_multiple_files(file_structure: FileStructure) -> None:
    file_structures = [
        file_structure,
        file_structure,
    ]
    with patch("aiofiles.open", MagicMock()) as mock_open:
        mock_file = AsyncMock()
        mock_open.return_value.__aenter__.return_value = mock_file
        await _write_files(file_structures)
        assert mock_open.call_count == 2
