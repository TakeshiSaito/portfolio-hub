from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_create_sample():
    applications.create_sample()

    [project] = applications.list_projects()
    [environment] = applications.list_environments()
    assert project.name == "sample_project"
    assert environment.project_id == project.id
    assert environment.name == "sample_environment"
    assert environment.packages == (dto.Package(name="hello", version="1.0.0"),)
    assert environment.tools == ("hello",)
    assert environment.default_tool == "hello"
