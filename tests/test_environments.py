from uuid import uuid4

import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto
from portfolio_hub.environment import EnvironmentAlreadyExistsError, EnvironmentNotFoundError
from portfolio_hub.project import ProjectNotFoundError


def test_create_environment(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0"), ("greeter_plugin", "1.0.0")], tools=["greet", "cheer"], default_tool="cheer")

    [saved] = applications.list_environments()
    assert saved.id == environment.id
    assert saved.project_id == project.id
    assert saved.name == "anim"
    assert saved.default_tool == "cheer"
    assert set(saved.packages) == {dto.Package(name="greeter", version="2.0.0"), dto.Package(name="greeter_plugin", version="1.0.0")}
    assert set(saved.tools) == {"greet", "cheer"}


@pytest.mark.parametrize("name", ["sample", "Sample_2", "__", "A0", "layout_v2", "a" * 64])
def test_create_environment_with_a_name_of_letters_digits_and_underscores(project: dto.Project, name: str):
    assert applications.create_environment(project.id, name, [("greeter", "2.0.0")]).name == name


@pytest.mark.parametrize("name", ["", "_", "A", "0", "a" * 65, "sample project", "sample-project", "sample.v2", "サンプル", "ｓａｍｐｌｅ", " sample", "sample\n"])
def test_create_environment_with_any_other_character_in_the_name_fails(project: dto.Project, name: str):
    with pytest.raises(ValueError):
        applications.create_environment(project.id, name, [("greeter", "2.0.0")])


def test_create_environment_in_an_unknown_project_fails():
    with pytest.raises(ProjectNotFoundError):
        applications.create_environment(uuid4(), "anim", [("greeter", "2.0.0")])


def test_create_environment_with_an_existing_name_in_the_project_fails(project: dto.Project):
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    with pytest.raises(EnvironmentAlreadyExistsError):
        applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])


def test_create_environment_with_the_name_of_one_in_another_project(project: dto.Project):
    other = applications.create_project("other_project")
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    environment = applications.create_environment(other.id, "anim", [("greeter", "2.0.0")])

    assert environment.id in [e.id for e in applications.list_environments()]


def test_create_environment_without_a_package_fails(project: dto.Project):
    with pytest.raises(ValueError):
        applications.create_environment(project.id, "anim", [])


def test_create_environment_with_the_same_package_twice_fails(project: dto.Project):
    with pytest.raises(ValueError):
        applications.create_environment(project.id, "anim", [("greeter", "1.0.0"), ("greeter", "2.0.0")])


@pytest.mark.parametrize("package", [("greeter loud", "2.0.0"), ("", "2.0.0"), ("greeter", "")])
def test_create_environment_with_an_invalid_package_fails(project: dto.Project, package: tuple[str, str]):
    with pytest.raises(ValueError):
        applications.create_environment(project.id, "anim", [package])


@pytest.mark.parametrize("tool", ["", "greet loud", "g" * 65])
def test_create_environment_with_an_invalid_tool_name_fails(project: dto.Project, tool: str):
    with pytest.raises(ValueError):
        applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=[tool])


def test_create_environment_with_the_same_tool_twice_fails(project: dto.Project):
    with pytest.raises(ValueError):
        applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet", "greet"])


def test_create_environment_without_a_default_tool_defaults_to_terminal(project: dto.Project):
    assert applications.create_environment(project.id, "anim", [("greeter", "2.0.0")]).default_tool == "terminal"


def test_create_environment_with_a_default_tool_that_is_not_one_of_the_tools_fails(project: dto.Project):
    with pytest.raises(ValueError):
        applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"], default_tool="cheer")


def test_rename_environment_and_replace_its_packages_and_tools(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "1.0.0")], tools=["greet"], default_tool="greet")

    applications.rename_environment(environment.id, "layout")
    applications.replace_packages(environment.id, [("greeter_plugin", "1.0.0")])
    applications.replace_tools(environment.id, ["cheer"], default_tool="cheer")

    [saved] = applications.list_environments()
    assert saved.id == environment.id
    assert saved.name == "layout"
    assert saved.packages == (dto.Package(name="greeter_plugin", version="1.0.0"),)
    assert saved.tools == ("cheer",)
    assert saved.default_tool == "cheer"


def test_rename_environment_to_another_environments_name_in_the_project_fails(project: dto.Project):
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])
    layout = applications.create_environment(project.id, "layout", [("greeter", "2.0.0")])

    with pytest.raises(EnvironmentAlreadyExistsError):
        applications.rename_environment(layout.id, "anim")


def test_replace_packages_with_none_fails(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    with pytest.raises(ValueError):
        applications.replace_packages(environment.id, [])


def test_replace_tools_with_a_default_tool_that_is_not_one_of_them_fails(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"], default_tool="greet")

    with pytest.raises(ValueError):
        applications.replace_tools(environment.id, ["cheer"], default_tool="greet")


def test_delete_environment(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])
    assert environment.id in [e.id for e in applications.list_environments()]

    applications.delete_environment(environment.id)

    assert environment.id not in [e.id for e in applications.list_environments()]


def test_rename_unknown_environment_fails():
    with pytest.raises(EnvironmentNotFoundError):
        applications.rename_environment(uuid4(), "layout")


def test_replace_packages_of_an_unknown_environment_fails():
    with pytest.raises(EnvironmentNotFoundError):
        applications.replace_packages(uuid4(), [("greeter", "2.0.0")])


def test_replace_tools_of_an_unknown_environment_fails():
    with pytest.raises(EnvironmentNotFoundError):
        applications.replace_tools(uuid4(), ["greet"])


def test_delete_unknown_environment_fails():
    with pytest.raises(EnvironmentNotFoundError):
        applications.delete_environment(uuid4())


def test_launch_unknown_environment_fails():
    with pytest.raises(EnvironmentNotFoundError):
        applications.launch(uuid4(), "greet")
