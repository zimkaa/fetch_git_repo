import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from tests.conftest import ORIGINAL_STRING
from src.main import _write_file


@pytest.mark.asyncio()
async def test_write_file_success() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"

        with patch("aiofiles.open", MagicMock()) as mock_open:
            await _write_file(ORIGINAL_STRING, test_file)

        mock_open.assert_called_once_with(test_file, "w")
        mock_open.return_value.__aenter__.return_value.write.assert_called_once_with(
            ORIGINAL_STRING,
        )


@pytest.mark.asyncio()
async def test_write_file_exception() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"

        with patch(
            "aiofiles.open",
            MagicMock(side_effect=IOError("Failed to write"))
        ) as mock_open:
            with pytest.raises(IOError):
                await _write_file(ORIGINAL_STRING, test_file)

        mock_open.assert_called_once_with(test_file, "w")
