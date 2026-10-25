from collections.abc import Callable, Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from portfolio_hub.http import create_app

type Given = Callable[[str, dict[str, Any]], Any]


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app(), base_url="http://127.0.0.1") as client:
        yield client


@pytest.fixture
def given(client: TestClient) -> Given:
    def post(url: str, body: dict[str, Any]) -> Any:
        response = client.post(url, json=body)
        assert response.status_code == 201
        return response.json()

    return post


@pytest.fixture
def project(given: Given) -> dict[str, Any]:
    return given("/api/projects", {"name": "sample_project"})
