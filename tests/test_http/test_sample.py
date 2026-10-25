from pathlib import Path

from fastapi.testclient import TestClient

from portfolio_hub.http import create_app


def test_start_without_a_database_creates_the_sample(database: Path):
    database.unlink()

    with TestClient(create_app(), base_url="http://127.0.0.1") as client:
        response = client.get("/api/projects")

    body = response.json()
    assert response.status_code == 200
    assert body == [{"id": body[0]["id"], "name": "sample_project"}]
