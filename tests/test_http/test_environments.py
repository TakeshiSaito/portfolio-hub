from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient


def test_get_environments(client: TestClient, given, project: dict[str, Any]):
    environment = given(f"/api/projects/{project['id']}/environments", {"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}], "tools": ["greet"], "default_tool": "greet"})
    other = given("/api/projects", {"name": "other_project"})
    given(f"/api/projects/{other['id']}/environments", {"name": "layout", "packages": [{"name": "greeter", "version": "2.0.0"}]})

    response = client.get(f"/api/projects/{project['id']}/environments")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": environment["id"],
            "project_id": project["id"],
            "name": "anim",
            "packages": [{"name": "greeter", "version": "2.0.0"}],
            "tools": ["greet"],
            "default_tool": "greet",
        }
    ]


def test_get_environments_of_an_unknown_project_is_not_found(client: TestClient):
    project_id = uuid4()

    response = client.get(f"/api/projects/{project_id}/environments")

    assert response.status_code == 404
    assert response.json() == {"detail": f"project {project_id} does not exist"}


def test_get_environments_of_an_invalid_project_id_is_unprocessable(client: TestClient):
    response = client.get("/api/projects/not-a-uuid/environments")

    assert response.status_code == 422
    assert response.json() == {"detail": "Input should be a valid UUID, invalid character: found `n` at 0"}


def test_post_environments(client: TestClient, project: dict[str, Any]):
    response = client.post(
        f"/api/projects/{project['id']}/environments",
        json={"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}], "tools": ["greet"], "default_tool": "greet"},
    )

    body = response.json()
    assert response.status_code == 201
    assert body == {
        "id": body["id"],
        "project_id": project["id"],
        "name": "anim",
        "packages": [{"name": "greeter", "version": "2.0.0"}],
        "tools": ["greet"],
        "default_tool": "greet",
    }
    assert client.get(f"/api/projects/{project['id']}/environments").json() == [body]


def test_post_environments_in_an_unknown_project_is_not_found(client: TestClient):
    project_id = uuid4()

    response = client.post(f"/api/projects/{project_id}/environments", json={"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}]})

    assert response.status_code == 404
    assert response.json() == {"detail": f"project {project_id} does not exist"}


def test_post_environments_without_a_package_is_unprocessable(client: TestClient, project: dict[str, Any]):
    response = client.post(f"/api/projects/{project['id']}/environments", json={"name": "anim", "packages": []})

    assert response.status_code == 422
    assert response.json() == {"detail": "an environment needs at least one package"}
    assert client.get(f"/api/projects/{project['id']}/environments").json() == []


def test_post_environments_with_an_existing_name_conflicts(client: TestClient, given, project: dict[str, Any]):
    given(f"/api/projects/{project['id']}/environments", {"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}]})

    response = client.post(f"/api/projects/{project['id']}/environments", json={"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}]})

    assert response.status_code == 409
    assert response.json() == {"detail": "the project already has an environment named anim"}


def test_put_environment_name(client: TestClient, given, project: dict[str, Any]):
    environment = given(f"/api/projects/{project['id']}/environments", {"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}]})

    response = client.put(f"/api/environments/{environment['id']}/name", json={"name": "layout"})

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/projects/{project['id']}/environments").json() == [{**environment, "name": "layout"}]


def test_put_environment_packages(client: TestClient, given, project: dict[str, Any]):
    environment = given(f"/api/projects/{project['id']}/environments", {"name": "anim", "packages": [{"name": "greeter", "version": "1.0.0"}]})

    response = client.put(f"/api/environments/{environment['id']}/packages", json={"packages": [{"name": "greeter_plugin", "version": "1.0.0"}]})

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/projects/{project['id']}/environments").json() == [{**environment, "packages": [{"name": "greeter_plugin", "version": "1.0.0"}]}]


def test_put_environment_tools(client: TestClient, given, project: dict[str, Any]):
    environment = given(f"/api/projects/{project['id']}/environments", {"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}], "tools": ["greet"], "default_tool": "greet"})

    response = client.put(f"/api/environments/{environment['id']}/tools", json={"tools": ["cheer"], "default_tool": "cheer"})

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/projects/{project['id']}/environments").json() == [{**environment, "tools": ["cheer"], "default_tool": "cheer"}]


def test_put_environment_tools_with_a_default_tool_that_is_not_one_of_them_is_unprocessable(client: TestClient, given, project: dict[str, Any]):
    environment = given(f"/api/projects/{project['id']}/environments", {"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}]})

    response = client.put(f"/api/environments/{environment['id']}/tools", json={"tools": ["greet"], "default_tool": "cheer"})

    assert response.status_code == 422
    assert response.json() == {"detail": "default tool cheer is not one of the tools"}


def test_delete_environment(client: TestClient, given, project: dict[str, Any]):
    environment = given(f"/api/projects/{project['id']}/environments", {"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}]})

    response = client.delete(f"/api/environments/{environment['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/projects/{project['id']}/environments").json() == []


def test_delete_unknown_environment_is_not_found(client: TestClient):
    environment_id = uuid4()

    response = client.delete(f"/api/environments/{environment_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"environment {environment_id} does not exist"}
