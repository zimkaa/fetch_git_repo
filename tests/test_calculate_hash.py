import hashlib
import tempfile
from pathlib import Path

import pytest

from src.main import _calculate_hash


def test_calculate_hash_with_known_content() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test_file.txt"
        file_path.write_text("Hello, world!")
        expected_hash = hashlib.sha256(b"Hello, world!").hexdigest()
        calculated_hash = _calculate_hash(
            str(file_path.name),
            temp_project_folder=Path(temp_dir),
        )
        assert calculated_hash == expected_hash


def test_calculate_hash_non_existent_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(FileNotFoundError):
            _calculate_hash("non_existent_file.txt", temp_project_folder=Path(temp_dir))


def test_calculate_hash_empty_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "empty_file.txt"
        file_path.touch()
        expected_hash = hashlib.sha256(b"").hexdigest()
        calculated_hash = _calculate_hash(
            str(file_path.name),
            temp_project_folder=Path(temp_dir),
        )
        assert calculated_hash == expected_hash
