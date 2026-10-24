from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_get_projects(client: TestClient):
    project = applications.create_project("sample_project")

    response = client.get("/api/projects")

    assert response.status_code == 200
    assert response.json() == [{"id": str(project.id), "name": "sample_project"}]


def test_post_projects(client: TestClient):
    response = client.post("/api/projects", json={"name": "sample_project"})

    [project] = applications.list_projects()
    assert response.status_code == 201
    assert response.json() == {"id": str(project.id), "name": "sample_project"}


def test_post_projects_with_environments(client: TestClient):
    response = client.post(
        "/api/projects",
        json={
            "name": "sample_project",
            "environments": [{"name": "anim", "packages": [{"name": "greeter", "version": "2.0.0"}], "tools": ["greet"], "default_tool": "greet"}],
        },
    )

    [project] = applications.list_projects()
    [environment] = applications.list_environments()
    assert response.status_code == 201
    assert response.json() == {"id": str(project.id), "name": "sample_project"}
    assert environment == dto.Environment(
        id=environment.id,
        project_id=project.id,
        name="anim",
        packages=(dto.Package(name="greeter", version="2.0.0"),),
        tools=("greet",),
        default_tool="greet",
    )


def test_post_projects_with_an_invalid_name_is_unprocessable(client: TestClient):
    response = client.post("/api/projects", json={"name": "sample project"})

    assert response.status_code == 422
    assert response.json() == {"detail": "String should match pattern '^[A-Za-z0-9_]+$'"}
    assert applications.list_projects() == []


def test_post_projects_with_an_existing_name_conflicts(client: TestClient, project: dto.Project):
    response = client.post("/api/projects", json={"name": "sample_project"})

    assert response.status_code == 409
    assert response.json() == {"detail": "project sample_project already exists"}


def test_put_project_name(client: TestClient, project: dto.Project):
    response = client.put(f"/api/projects/{project.id}/name", json={"name": "renamed"})

    assert response.status_code == 204
    assert response.content == b""
    assert applications.list_projects() == [dto.Project(id=project.id, name="renamed")]


def test_put_project_name_of_an_unknown_project_is_not_found(client: TestClient):
    project_id = uuid4()

    response = client.put(f"/api/projects/{project_id}/name", json={"name": "renamed"})

    assert response.status_code == 404
    assert response.json() == {"detail": f"project {project_id} does not exist"}


def test_delete_project(client: TestClient, project: dto.Project):
    response = client.delete(f"/api/projects/{project.id}")

    assert response.status_code == 204
    assert response.content == b""
    assert applications.list_projects() == []


def test_delete_unknown_project_is_not_found(client: TestClient):
    project_id = uuid4()

    response = client.delete(f"/api/projects/{project_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"project {project_id} does not exist"}


def test_get_projects_from_another_host_is_bad_request(client: TestClient):
    response = client.get("/api/projects", headers={"Host": "evil.example"})

    assert response.status_code == 400
    assert response.text == "Invalid host header"


@pytest.mark.parametrize("host", ["127.0.0.1:8000", "localhost:8000"])
def test_get_projects_from_this_machine(client: TestClient, host: str):
    response = client.get("/api/projects", headers={"Host": host})

    assert response.status_code == 200
