import tempfile
from pathlib import Path

from src.main import _create_empty_file


def test_create_empty_file_creates_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_project_folder = Path(temp_dir)
        test_file_path = "test_file.txt"

        _create_empty_file(test_file_path, temp_project_folder)
        expected_path = temp_project_folder / test_file_path

        assert expected_path.exists()
    assert expected_path.exists() is False


def test_create_empty_file_creates_directories() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_project_folder = Path(temp_dir)
        test_file_path = "dir1/dir2/test_file.txt"

        _create_empty_file(test_file_path, temp_project_folder)
        expected_path = temp_project_folder / test_file_path

        assert expected_path.parent.exists()
        assert expected_path.exists()
    assert expected_path.exists() is False


def test_create_empty_file_with_existing_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_project_folder = Path(temp_dir)
        test_file_path = "test_file.txt"
        expected_path = temp_project_folder / test_file_path
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.touch(exist_ok=True)

        _create_empty_file(test_file_path, temp_project_folder)

        assert expected_path.exists()
    assert expected_path.exists() is False
