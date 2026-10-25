from uuid import uuid4

from fastapi.testclient import TestClient

from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_get_resolved_packages(client: TestClient, project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter_plugin", "1.0.0")])

    response = client.get(f"/api/environments/{environment.id}/resolved-packages")

    assert response.status_code == 200
    assert response.json() == [{"name": "greeter", "version": "2.0.0"}, {"name": "greeter_plugin", "version": "1.0.0"}]


def test_get_resolved_packages_of_conflicting_packages_is_unprocessable(client: TestClient, project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "1.0.0"), ("greeter_plugin", "1.0.0")])

    response = client.get(f"/api/environments/{environment.id}/resolved-packages")

    assert response.status_code == 422
    assert response.json() == {"detail": "The following package conflicts occurred: (greeter-2 <--!--> greeter==1.0.0)"}


def test_get_resolved_packages_of_an_unknown_environment_is_not_found(client: TestClient):
    environment_id = uuid4()

    response = client.get(f"/api/environments/{environment_id}/resolved-packages")

    assert response.status_code == 404
    assert response.json() == {"detail": f"environment {environment_id} does not exist"}


def test_post_launches(client: TestClient, project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"])

    response = client.post(f"/api/environments/{environment.id}/launches", json={"tool": "greet"})

    body = response.json()
    assert response.status_code == 201
    assert body["pid"] > 0
    assert body == {"tool": "greet", "pid": body["pid"], "resolved_packages": [{"name": "greeter", "version": "2.0.0"}]}


def test_post_launches_in_an_unknown_environment_is_not_found(client: TestClient):
    environment_id = uuid4()

    response = client.post(f"/api/environments/{environment_id}/launches", json={"tool": "greet"})

    assert response.status_code == 404
    assert response.json() == {"detail": f"environment {environment_id} does not exist"}


def test_post_launches_with_an_unregistered_tool_is_unprocessable(client: TestClient, project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"])

    response = client.post(f"/api/environments/{environment.id}/launches", json={"tool": "nosuchtool"})

    assert response.status_code == 422
    assert response.json() == {"detail": "tool nosuchtool is not one of the tools of environment anim"}
