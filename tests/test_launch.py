import time
from pathlib import Path

import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto
from portfolio_hub.environment import ToolNotRegisteredError
from portfolio_hub.launcher import FailedToResolveError


def test_launch(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"])

    result = applications.launch(environment.id, "greet")

    assert result.pid > 0


@pytest.mark.parametrize("version", ["1.0.0", "2.0.0"])
def test_launch_uses_the_chosen_version(project: dto.Project, version: str):
    environment = applications.create_environment(project.id, "anim", [("greeter", version)], tools=["greet"])

    result = applications.launch(environment.id, "greet")

    assert dto.Package(name="greeter", version=version) in result.resolved_packages


def test_launch_resolves_the_requirements_of_a_package(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter_plugin", "1.0.0")], tools=["cheer"])

    result = applications.launch(environment.id, "cheer")

    assert {dto.Package(name="greeter_plugin", version="1.0.0"), dto.Package(name="greeter", version="2.0.0")} <= set(result.resolved_packages)


def test_launch_with_conflicting_packages_fails(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "1.0.0"), ("greeter_plugin", "1.0.0")], tools=["cheer"])

    with pytest.raises(FailedToResolveError):
        applications.launch(environment.id, "cheer")


def test_launch_unregistered_tool_fails(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"])

    with pytest.raises(ToolNotRegisteredError):
        applications.launch(environment.id, "nosuchtool")


def test_launch_without_a_tool_runs_the_default_tool(project: dto.Project, capfd: pytest.CaptureFixture[str]):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"], default_tool="greet")

    result = applications.launch(environment.id)

    assert result.tool == "greet"
    out = ""
    for _ in range(100):
        out += capfd.readouterr().out
        if out.endswith("\n"):
            break
        time.sleep(0.1)
    assert out == "Hello, world! (greeter 2.0.0)\n"


def test_launch_without_a_tool_opens_a_terminal(project: dto.Project, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    record = tmp_path / "record"
    monkeypatch.setenv("PORTFOLIO_HUB_TEST_RECORD", str(record))
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    applications.launch(environment.id)

    for _ in range(100):
        if record.exists() and record.read_text().endswith("\n"):
            break
        time.sleep(0.1)
    assert record.read_text() == "2.0.0\n"


def test_launch_terminal_when_the_default_tool_is_another_tool(project: dto.Project, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    record = tmp_path / "record"
    monkeypatch.setenv("PORTFOLIO_HUB_TEST_RECORD", str(record))
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"], default_tool="greet")

    result = applications.launch(environment.id, "terminal")

    assert result.tool == "terminal"
    for _ in range(100):
        if record.exists() and record.read_text().endswith("\n"):
            break
        time.sleep(0.1)
    assert record.read_text() == "2.0.0\n"


def test_launch_with_a_missing_package_fails(project: dto.Project):
    environment = applications.create_environment(project.id, "anim", [("greeter", "9.9.9")], tools=["greet"])

    with pytest.raises(FailedToResolveError):
        applications.launch(environment.id, "greet")
