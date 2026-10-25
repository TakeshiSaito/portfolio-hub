from pathlib import Path

from fastapi.testclient import TestClient

from portfolio_hub.http import create_app


def test_get_openapi_json_has_an_example_for_creating_a_project(client: TestClient):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["components"]["schemas"]["NewProject"] == {
        "properties": {
            "name": {"type": "string", "title": "Name", "examples": ["foo"]},
            "environments": {"items": {"$ref": "#/components/schemas/NewEnvironment"}, "type": "array", "title": "Environments", "default": []},
        },
        "type": "object",
        "required": ["name"],
        "title": "NewProject",
    }


def test_post_projects_with_the_example_in_the_docs(database: Path):
    database.unlink()

    with TestClient(create_app(), base_url="http://127.0.0.1") as client:
        schemas = client.get("/openapi.json").json()["components"]["schemas"]
        environment = {name: field["examples"][0] for name, field in schemas["NewEnvironment"]["properties"].items()}
        body = {"name": schemas["NewProject"]["properties"]["name"]["examples"][0], "environments": [environment]}
        response = client.post("/api/projects", json=body)

    assert response.status_code == 201


def test_get_openapi_json_explains_how_to_open_a_terminal_when_launching(client: TestClient):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["components"]["schemas"]["NewLaunch"] == {
        "properties": {
            "tool": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "Name of the tool to launch, or terminal to open a terminal in the environment. Omit it to launch the default tool of the environment.",
                "examples": ["greet"],
                "title": "Tool",
            }
        },
        "title": "NewLaunch",
        "type": "object",
    }


def test_get_docs_enables_try_it_out(client: TestClient):
    response = client.get("/docs")

    assert response.status_code == 200
    assert '"tryItOutEnabled": true' in response.text


def test_get_openapi_json_shows_the_version(client: TestClient, project_metadata: dict[str, str]):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"] == {
        "title": project_metadata["name"],
        "description": project_metadata["description"],
        "version": project_metadata["version"],
    }
