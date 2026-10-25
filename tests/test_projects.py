from uuid import uuid4

import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto
from portfolio_hub.environment import EnvironmentAlreadyExistsError, EnvironmentNotFoundError
from portfolio_hub.project import ProjectAlreadyExistsError, ProjectNotFoundError


def test_create_project():
    project = applications.create_project("sample_project")

    assert applications.list_projects() == [dto.Project(id=project.id, name="sample_project")]


def test_create_project_with_environments():
    project = applications.create_project(
        "sample_project",
        environments=[
            dto.NewEnvironment(name="anim", packages=[dto.Package(name="greeter", version="2.0.0")], tools=["greet"], default_tool="greet"),
            dto.NewEnvironment(name="layout", packages=[dto.Package(name="greeter", version="1.0.0")]),
        ],
    )

    [anim, layout] = applications.list_environments(project.id)
    assert anim == dto.Environment(
        id=anim.id,
        project_id=project.id,
        name="anim",
        packages=(dto.Package(name="greeter", version="2.0.0"),),
        tools=("greet",),
        default_tool="greet",
    )
    assert layout == dto.Environment(
        id=layout.id,
        project_id=project.id,
        name="layout",
        packages=(dto.Package(name="greeter", version="1.0.0"),),
        tools=(),
        default_tool="terminal",
    )


def test_create_project_with_two_environments_of_the_same_name_fails():
    environments = [
        dto.NewEnvironment(name="anim", packages=[dto.Package(name="greeter", version="2.0.0")]),
        dto.NewEnvironment(name="anim", packages=[dto.Package(name="greeter", version="1.0.0")]),
    ]

    with pytest.raises(EnvironmentAlreadyExistsError):
        applications.create_project("sample_project", environments=environments)

    assert applications.list_projects() == []


@pytest.mark.parametrize("name", ["sample", "Sample_2", "__", "A0", "layout_v2", "a" * 64])
def test_create_project_with_a_name_of_letters_digits_and_underscores(name: str):
    assert applications.create_project(name).name == name


@pytest.mark.parametrize("name", ["", "_", "A", "0", "a" * 65, "sample project", "sample-project", "sample.v2", "サンプル", "ｓａｍｐｌｅ", " sample", "sample\n"])
def test_create_project_with_any_other_character_in_the_name_fails(name: str):
    with pytest.raises(ValueError):
        applications.create_project(name)


def test_create_project_with_an_existing_name_fails(project: dto.Project):
    assert project in applications.list_projects()

    with pytest.raises(ProjectAlreadyExistsError):
        applications.create_project("sample_project", environments=[dto.NewEnvironment(name="anim", packages=[dto.Package(name="greeter", version="2.0.0")])])

    assert applications.list_environments(project.id) == []


def test_rename_project(project: dto.Project):
    applications.rename_project(project.id, "renamed")

    assert applications.list_projects() == [dto.Project(id=project.id, name="renamed")]


def test_rename_project_to_its_own_name(project: dto.Project):
    applications.rename_project(project.id, "sample_project")

    assert applications.list_projects() == [dto.Project(id=project.id, name="sample_project")]


def test_rename_project_to_another_projects_name_fails(project: dto.Project):
    other = applications.create_project("other_project")

    with pytest.raises(ProjectAlreadyExistsError):
        applications.rename_project(other.id, "sample_project")


def test_rename_project_to_an_invalid_name_fails(project: dto.Project):
    with pytest.raises(ValueError):
        applications.rename_project(project.id, "sample project")


def test_delete_project(project: dto.Project):
    assert project in applications.list_projects()

    applications.delete_project(project.id)

    assert project not in applications.list_projects()


def test_delete_project_deletes_its_environments(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])
    assert environment.id in [e.id for e in applications.list_environments(project.id)]

    applications.delete_project(project.id)

    with pytest.raises(EnvironmentNotFoundError):
        applications.resolve_environment(environment.id)


def test_delete_project_keeps_the_environments_of_other_projects(project: dto.Project):
    other = applications.create_project("other_project")
    kept = applications.create_environment(other.id, "anim", [("greeter", "2.0.0")])

    applications.delete_project(project.id)

    assert kept.id in [e.id for e in applications.list_environments(other.id)]


def test_rename_unknown_project_fails():
    with pytest.raises(ProjectNotFoundError):
        applications.rename_project(uuid4(), "renamed")


def test_delete_unknown_project_fails():
    with pytest.raises(ProjectNotFoundError):
        applications.delete_project(uuid4())
