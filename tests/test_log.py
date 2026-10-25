import logging

import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_launch_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"])
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    result = applications.launch(environment.id, "greet")

    assert caplog.messages == [f"launched greet in environment anim ({environment.id}) with pid {result.pid}"]


def test_create_environment_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    assert caplog.messages == [f"created environment anim ({environment.id}) in project sample_project"]


def test_create_project_writes_a_log(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO, logger="portfolio_hub")

    project = applications.create_project("sample_project")

    assert caplog.messages == [f"created project sample_project ({project.id})"]


def test_create_project_with_environments_writes_a_log(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO, logger="portfolio_hub")

    project = applications.create_project("sample_project", environments=[dto.NewEnvironment(name="anim", packages=[dto.Package(name="greeter", version="2.0.0")])])

    [environment] = applications.list_environments(project.id)
    assert caplog.messages == [
        f"created project sample_project ({project.id})",
        f"created environment anim ({environment.id}) in project sample_project",
    ]


def test_rename_project_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    applications.rename_project(project.id, "renamed")

    assert caplog.messages == [f"renamed project sample_project to renamed ({project.id})"]


def test_delete_project_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    applications.delete_project(project.id)

    assert caplog.messages == [
        f"deleted environment anim ({environment.id})",
        f"deleted project sample_project ({project.id})",
    ]


def test_rename_environment_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    applications.rename_environment(environment.id, "layout")

    assert caplog.messages == [f"renamed environment anim to layout ({environment.id})"]


def test_replace_packages_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    applications.replace_packages(environment.id, [("greeter_plugin", "1.0.0")])

    assert caplog.messages == [f"replaced the packages of environment anim ({environment.id}) with greeter_plugin 1.0.0"]


def test_replace_tools_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    applications.replace_tools(environment.id, ["greet"], "greet")

    assert caplog.messages == [f"replaced the tools of environment anim ({environment.id}) with greet; default tool greet"]


def test_delete_environment_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    applications.delete_environment(environment.id)

    assert caplog.messages == [f"deleted environment anim ({environment.id})"]
