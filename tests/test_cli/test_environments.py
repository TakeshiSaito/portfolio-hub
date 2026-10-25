import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_list_environments(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    applications.create_environment(project.id, "anim", [("greeter_plugin", "1.0.0"), ("greeter", "2.0.0")], tools=["greet", "cheer"], default_tool="cheer")
    applications.create_environment(project.id, "layout", [("greeter", "2.0.0")])
    other = applications.create_project("other_project")
    applications.create_environment(other.id, "fx", [("greeter", "2.0.0")])

    assert cli("phub environments list sample_project") == 0

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name    packages                             tools         default tool",
        " anim    greeter 2.0.0, greeter_plugin 1.0.0  cheer, greet  cheer",
        " layout  greeter 2.0.0                                      terminal",
    ]


def test_list_environments_of_an_unknown_project_fails(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub environments list unknown") == 1

    assert capsys.readouterr().err == "project unknown does not exist\n"


def test_create_environment(cli, project: dto.Project):
    assert cli("phub environments create sample_project anim --package greeter 2.0.0 --tool greet --default-tool greet") == 0

    [environment] = applications.list_environments()
    assert environment.project_id == project.id
    assert environment.name == "anim"
    assert environment.packages == (dto.Package(name="greeter", version="2.0.0"),)
    assert environment.tools == ("greet",)
    assert environment.default_tool == "greet"


def test_create_environment_without_a_package_fails(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    assert cli("phub environments create sample_project anim") == 1

    assert capsys.readouterr().err == "an environment needs at least one package\n"
    assert applications.list_environments() == []


def test_create_environment_in_an_unknown_project_fails(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub environments create unknown anim --package greeter 2.0.0") == 1

    assert capsys.readouterr().err == "project unknown does not exist\n"
    assert applications.list_environments() == []


def test_rename_environment(cli, project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    assert cli("phub environments rename sample_project anim layout") == 0

    assert [(e.id, e.name) for e in applications.list_environments()] == [(environment.id, "layout")]


def test_set_packages(cli, project: dto.Project):
    applications.create_environment(project.id, "anim", [("greeter", "1.0.0")])

    assert cli("phub environments set-packages sample_project anim --package greeter_plugin 1.0.0") == 0

    [environment] = applications.list_environments()
    assert environment.packages == (dto.Package(name="greeter_plugin", version="1.0.0"),)


def test_set_packages_without_a_package_fails(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    applications.create_environment(project.id, "anim", [("greeter", "1.0.0")])

    assert cli("phub environments set-packages sample_project anim") == 1

    assert capsys.readouterr().err == "an environment needs at least one package\n"


def test_set_tools(cli, project: dto.Project):
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"], default_tool="greet")

    assert cli("phub environments set-tools sample_project anim --tool cheer --default-tool cheer") == 0

    [environment] = applications.list_environments()
    assert environment.tools == ("cheer",)
    assert environment.default_tool == "cheer"


def test_set_tools_with_a_default_tool_that_is_not_one_of_them_fails(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    assert cli("phub environments set-tools sample_project anim --tool greet --default-tool cheer") == 1

    assert capsys.readouterr().err == "default tool cheer is not one of the tools\n"


def test_delete_environment(cli, project: dto.Project):
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    assert cli("phub environments delete sample_project anim") == 0

    assert applications.list_environments() == []


def test_delete_unknown_environment_fails(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    assert cli("phub environments delete sample_project unknown") == 1

    assert capsys.readouterr().err == "environment unknown does not exist in project sample_project\n"
