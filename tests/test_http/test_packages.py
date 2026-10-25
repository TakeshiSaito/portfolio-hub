from fastapi.testclient import TestClient


def test_get_packages(client: TestClient):
    response = client.get("/api/packages")

    assert response.status_code == 200
    assert sorted(response.json(), key=lambda p: (p["name"], p["version"])) == [
        {"name": "greeter", "version": "1.0.0"},
        {"name": "greeter", "version": "2.0.0"},
        {"name": "greeter_plugin", "version": "1.0.0"},
        {"name": "hello", "version": "1.0.0"},
    ]
