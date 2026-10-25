from uuid import uuid4

import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto
from portfolio_hub.environment import EnvironmentNotFoundError
from portfolio_hub.launcher import FailedToResolveError


@pytest.mark.parametrize("version", ["1.0.0", "2.0.0"])
def test_resolve_environment_uses_the_chosen_version(project: dto.Project, version: str):
    environment = applications.create_environment(project.id, "anim", [("greeter", version)])

    assert dto.Package(name="greeter", version=version) in applications.resolve_environment(environment.id)


def test_resolve_environment_resolves_the_requirements_of_a_package(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter_plugin", "1.0.0")])

    assert {dto.Package(name="greeter_plugin", version="1.0.0"), dto.Package(name="greeter", version="2.0.0")} <= set(applications.resolve_environment(environment.id))


def test_resolve_environment_with_conflicting_packages_fails(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "1.0.0"), ("greeter_plugin", "1.0.0")])

    with pytest.raises(FailedToResolveError):
        applications.resolve_environment(environment.id)


def test_resolve_unknown_environment_fails():
    with pytest.raises(EnvironmentNotFoundError):
        applications.resolve_environment(uuid4())


@pytest.mark.parametrize("package", [("greeter", "9.9.9"), ("nosuchpackage", "1.0.0")], ids=["missing version", "missing package"])
def test_resolve_environment_with_a_missing_package_fails(project: dto.Project, package: tuple[str, str]):
    environment = applications.create_environment(project.id, "anim", [package])

    with pytest.raises(FailedToResolveError):
        applications.resolve_environment(environment.id)
