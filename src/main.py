from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
from itertools import batched
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Final

import aiofiles
from aiohttp import ClientSession, ClientTimeout

from src.my_types import FileStructure, ResponseStructure, TreeElement

HEADERS: Final[dict] = {"accept": "application/json"}

URL: Final[str] = (
    "https://gitea.radium.group/api/v1/repos/radium/project-configuration/git/trees/HEAD?recursive=true"
)

TEMP_FOLDER = Path("/tmp")

TEMP_PROJECT_FOLDER = TEMP_FOLDER / Path("fetch_git_repo")

fmt = "%(asctime)s | %(levelname)8s | %(filename)s:%(lineno)3d | %(message)s"
formatter = logging.Formatter(fmt)

logging.basicConfig(level=logging.INFO, format=fmt)
logger = logging.getLogger(__name__)

request_handler = RotatingFileHandler("tests.log", maxBytes=5_242_880, backupCount=10)
request_handler.setFormatter(formatter)
logger.addHandler(request_handler)
logger.setLevel(logging.INFO)


async def _fetch_repo_structure(url: str, session: ClientSession) -> ResponseStructure:
    async with session.get(url, timeout=ClientTimeout(total=5)) as r:
        result = await r.json()

    return ResponseStructure(**result)


async def _download_file_structure(
    elements: tuple[TreeElement, ...],
    session: ClientSession,
) -> list[FileStructure]:
    file_structures = []
    for element in elements:
        async with session.get(element.url, timeout=ClientTimeout(total=5)) as r:
            result = await r.json()
            structure = FileStructure(**result, path=element.path)
            file_structures.append(structure)

    return file_structures


async def _write_file(text: str, path: Path) -> None:
    async with aiofiles.open(path, "w") as f:
        await f.write(text)


async def _write_files(files_list: list[FileStructure]) -> None:
    tasks = []
    for file_structure in files_list:
        decoded_str = base64.b64decode(file_structure.content).decode("utf-8")
        path = TEMP_PROJECT_FOLDER / Path(file_structure.path)
        tasks.append(asyncio.create_task(_write_file(decoded_str, path)))

    await asyncio.gather(*tasks)


def _calculate_hash(
    file: str,
    temp_project_folder: Path = TEMP_PROJECT_FOLDER,
) -> str:
    full_path = temp_project_folder / Path(file)
    with Path(full_path).open("rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _create_empty_file(
    file: str,
    temp_project_folder: Path = TEMP_PROJECT_FOLDER,
) -> None:
    full_path = temp_project_folder / Path(file)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch(exist_ok=True)


async def main() -> None:
    async with ClientSession(headers=HEADERS) as session:
        structure = await _fetch_repo_structure(url=URL, session=session)
        file_urls = []
        for item in structure.tree:
            if item.type == "blob":
                file_urls.append(item)
                _create_empty_file(item.path)

        batch_size = structure.total_count // 3  # 3 - stream
        assert (
            batch_size > 0
        ), "Repo doesn't have enough files to load parallel 3 - way stream"
        urls_batch1, urls_batch2, urls_batch3 = batched(file_urls, batch_size + 1)

        file_structures: list[FileStructure] = []
        for coro in asyncio.as_completed(
            [
                asyncio.create_task(_download_file_structure(urls_batch1, session)),
                asyncio.create_task(_download_file_structure(urls_batch2, session)),
                asyncio.create_task(_download_file_structure(urls_batch3, session)),
            ],
        ):
            part_file_structures = await coro
            file_structures.extend(part_file_structures)
            await _write_files(part_file_structures)

    for file_structure in file_structures:
        print_text = f"{file_structure.path} - {_calculate_hash(file_structure.path)}"
        logger.info(print_text)
