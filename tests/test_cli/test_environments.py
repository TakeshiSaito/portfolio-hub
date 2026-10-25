import pytest


def test_list_environments(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter_plugin 1.0.0 --package greeter 2.0.0 --tool greet --tool cheer --default-tool cheer")
    given("phub environments create sample_project layout --package greeter 2.0.0")
    given("phub projects create other_project")
    given("phub environments create other_project fx --package greeter 2.0.0")

    assert cli("phub environments list sample_project") == 0

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name    packages                             tools         default tool",
        " anim    greeter 2.0.0, greeter_plugin 1.0.0  cheer, greet  cheer",
        " layout  greeter 2.0.0                                      terminal",
    ]


def test_list_environments_of_an_unknown_project_fails(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub environments list unknown") == 1

    assert capsys.readouterr().err == "project unknown does not exist\n"


def test_create_environment(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")

    assert cli("phub environments create sample_project anim --package greeter 2.0.0 --tool greet --default-tool greet") == 0

    assert capsys.readouterr().out == "created environment anim in project sample_project\n"
    assert cli("phub environments list sample_project") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name  packages       tools  default tool",
        " anim  greeter 2.0.0  greet  greet",
    ]


def test_create_environment_without_a_package_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")

    assert cli("phub environments create sample_project anim") == 1

    assert capsys.readouterr().err == "an environment needs at least one package\n"
    assert cli("phub environments list sample_project") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name  packages  tools  default tool"]


def test_create_environment_in_an_unknown_project_fails(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub environments create unknown anim --package greeter 2.0.0") == 1

    assert capsys.readouterr().err == "project unknown does not exist\n"
    assert cli("phub projects list") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name"]


def test_rename_environment(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 2.0.0")

    assert cli("phub environments rename sample_project anim layout") == 0

    assert capsys.readouterr().out == "renamed environment anim to layout in project sample_project\n"
    assert cli("phub environments list sample_project") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name    packages       tools  default tool",
        " layout  greeter 2.0.0         terminal",
    ]


def test_set_packages(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 1.0.0")

    assert cli("phub environments set-packages sample_project anim --package greeter_plugin 1.0.0") == 0

    assert capsys.readouterr().out == "replaced the packages of environment anim in project sample_project\n"
    assert cli("phub environments list sample_project") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name  packages              tools  default tool",
        " anim  greeter_plugin 1.0.0         terminal",
    ]


def test_set_packages_without_a_package_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 1.0.0")

    assert cli("phub environments set-packages sample_project anim") == 1

    assert capsys.readouterr().err == "an environment needs at least one package\n"


def test_set_tools(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 2.0.0 --tool greet --default-tool greet")

    assert cli("phub environments set-tools sample_project anim --tool cheer --default-tool cheer") == 0

    assert capsys.readouterr().out == "replaced the tools of environment anim in project sample_project\n"
    assert cli("phub environments list sample_project") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name  packages       tools  default tool",
        " anim  greeter 2.0.0  cheer  cheer",
    ]


def test_set_tools_with_a_default_tool_that_is_not_one_of_them_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 2.0.0")

    assert cli("phub environments set-tools sample_project anim --tool greet --default-tool cheer") == 1

    assert capsys.readouterr().err == "default tool cheer is not one of the tools\n"


def test_delete_environment(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub environments create sample_project anim --package greeter 2.0.0")

    assert cli("phub environments delete sample_project anim") == 0

    assert capsys.readouterr().out == "deleted environment anim from project sample_project\n"
    assert cli("phub environments list sample_project") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name  packages  tools  default tool"]


def test_delete_unknown_environment_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")

    assert cli("phub environments delete sample_project unknown") == 1

    assert capsys.readouterr().err == "environment unknown does not exist in project sample_project\n"
