from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from portfolio_hub.http import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app(), base_url="http://127.0.0.1") as client:
        yield client
