from __future__ import annotations
import base64
from copy import deepcopy
from typing import Any

import pytest
from mimesis import Algorithm
from mimesis import Cryptographic
from mimesis import Internet
from mimesis import Numeric
from mimesis import Path
from mimesis.schema import Field
from mimesis.schema import Schema

from src.my_types import FileStructure
from src.my_types import ResponseStructure
from src.my_types import TreeElement


ORIGINAL_STRING = "Hello, World!"
byte_string = ORIGINAL_STRING.encode("utf-8")
text = base64.b64encode(byte_string).decode("utf-8")

crypto = Cryptographic()
internet = Internet()
field = Field("en")
path = Path()
number = Numeric()

file_schema = Schema(
    schema=lambda: {
        "content": text,
        "encoding": "base64",
        "url": internet.url(),
        "sha": crypto.hash(algorithm=Algorithm.SHA256),
        "size": number.integer_number(start=1, end=100),
        "path": "LICENSE",
    },
    iterations=1,
)

tree_element_blob = TreeElement(
    path="LICENSE",
    mode="100644",
    type="blob",
    size=823,
    sha="b9c199c98f9bec183a195a9c0afc0a2e4fcc7654",
    url="/git/blobs/b9c199c98f9bec183a195a9c0afc0a2e4fcc7654",
)

tree_element_tree = TreeElement(
    path="src",
    mode="100644",
    type="tree",
    size=0,
    sha="84220e02f05ca16fdae7f8dd37eca06899f53b25",
    url="/git/trees/84220e02f05ca16fdae7f8dd37eca06899f53b25",
)

response_schema = Schema(
    schema=lambda: {
        "tree": [
            tree_element_tree,
            *[tree_element_blob for _ in range(10)],
        ],
        "url": internet.url(),
        "sha": crypto.hash(algorithm=Algorithm.SHA256),
        "page": number.integer_number(start=1, end=100),
        "total_count": 11,
        "truncated": False,
    },
    iterations=1,
)


file_data = file_schema.create()[0]


@pytest.fixture()
def file_structure() -> FileStructure:
    return FileStructure(**file_data)


def get_file_dict() -> dict[str, Any]:
    new_file_data = deepcopy(file_data)
    new_file_data.pop("path")
    return new_file_data


response_data = response_schema.create()[0]


@pytest.fixture()
def response_structure_dict() -> dict[str, Any]:
    return ResponseStructure(**response_data).model_dump()


def get_response_structure_dict() -> dict[str, Any]:
    return ResponseStructure(**response_data).model_dump()


@pytest.fixture()
def get_response_structure() -> ResponseStructure:
    return ResponseStructure(**response_data)
