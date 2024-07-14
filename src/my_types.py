from __future__ import annotations

from pydantic import BaseModel


class FileStructure(BaseModel):
    content: str
    encoding: str
    url: str
    sha: str
    size: int
    path: str


class TreeElement(BaseModel):
    path: str
    mode: str
    type: str
    size: int
    sha: str
    url: str


class ResponseStructure(BaseModel):
    sha: str
    url: str
    tree: list[TreeElement]
    truncated: bool
    page: int
    total_count: int
