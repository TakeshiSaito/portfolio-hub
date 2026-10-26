import re
from pathlib import Path

import pytest


def test_resolve(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter_plugin 1.0.0")

    assert cli("phub resolve sample_project anim") == 0

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name            version",
        " greeter         2.0.0",
        " greeter_plugin  1.0.0",
    ]


def test_resolve_with_conflicting_packages_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 1.0.0 --package greeter_plugin 1.0.0")

    assert cli("phub resolve sample_project anim") == 1

    assert capsys.readouterr().err


def test_resolve_with_a_missing_package_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 9.9.9")

    assert cli("phub resolve sample_project anim") == 1

    assert capsys.readouterr().err == "Package could not be found: greeter==9.9.9\n"


def test_launch(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 2.0.0 --tool greet")

    assert cli("phub launch sample_project anim greet") == 0

    assert re.fullmatch(r"launched greet in environment anim of project sample_project \(pid \d+\)\n", capsys.readouterr().out)


def test_launch_without_a_tool(cli, given, capsys: pytest.CaptureFixture[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PORTFOLIO_HUB_TEST_RECORD", str(tmp_path / "record"))
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 2.0.0")

    assert cli("phub launch sample_project anim") == 0

    assert re.fullmatch(r"launched terminal in environment anim of project sample_project \(pid \d+\)\n", capsys.readouterr().out)


def test_launch_unregistered_tool_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 2.0.0 --tool greet")

    assert cli("phub launch sample_project anim nosuchtool") == 1

    assert capsys.readouterr().err == "tool nosuchtool is not one of the tools of environment anim\n"


def test_launch_unknown_environment_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")

    assert cli("phub launch sample_project unknown greet") == 1

    assert "unknown" in capsys.readouterr().err
