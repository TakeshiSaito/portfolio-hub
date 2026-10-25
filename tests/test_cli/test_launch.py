import re
from pathlib import Path

import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_resolve(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    applications.create_environment(project.id, "anim", [("greeter_plugin", "1.0.0")])

    assert cli("phub resolve sample_project anim") == 0

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name            version",
        " greeter         2.0.0",
        " greeter_plugin  1.0.0",
    ]


def test_resolve_with_conflicting_packages_fails(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    applications.create_environment(project.id, "anim", [("greeter", "1.0.0"), ("greeter_plugin", "1.0.0")])

    assert cli("phub resolve sample_project anim") == 1

    assert capsys.readouterr().err


def test_resolve_with_a_missing_package_fails(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    applications.create_environment(project.id, "anim", [("greeter", "9.9.9")])

    assert cli("phub resolve sample_project anim") == 1

    assert capsys.readouterr().err == "Package could not be found: greeter-9.9.9\n"


def test_launch(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"])

    assert cli("phub launch sample_project anim greet") == 0

    assert re.fullmatch(r"launched greet in environment anim of project sample_project \(pid \d+\)\n", capsys.readouterr().out)


def test_launch_without_a_tool(cli, project: dto.Project, capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PORTFOLIO_HUB_TEST_RECORD", str(tmp_path / "record"))
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")])

    assert cli("phub launch sample_project anim") == 0

    assert re.fullmatch(r"launched terminal in environment anim of project sample_project \(pid \d+\)\n", capsys.readouterr().out)


def test_launch_unregistered_tool_fails(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"])

    assert cli("phub launch sample_project anim nosuchtool") == 1

    assert capsys.readouterr().err == "tool nosuchtool is not one of the tools of environment anim\n"


def test_launch_unknown_environment_fails(cli, project: dto.Project, capsys: pytest.CaptureFixture[str]):
    assert cli("phub launch sample_project unknown greet") == 1

    assert "unknown" in capsys.readouterr().err
