import pytest


def test_list_projects(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")
    given("phub projects create fx_project")

    assert cli("phub projects list") == 0

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name", " sample_project", " fx_project"]


def test_create_project(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub projects create sample_project") == 0

    assert capsys.readouterr().out == "created project sample_project\n"
    assert cli("phub projects list") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name", " sample_project"]


def test_create_project_with_an_invalid_name_fails(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub projects create 'sample project'") == 1

    assert capsys.readouterr().err == "String should match pattern '^[A-Za-z0-9_]+$'\n"
    assert cli("phub projects list") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name"]


def test_create_project_with_an_existing_name_fails(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")

    assert cli("phub projects create sample_project") == 1

    assert capsys.readouterr().err == "project sample_project already exists\n"


def test_rename_project(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")

    assert cli("phub projects rename sample_project renamed") == 0

    assert capsys.readouterr().out == "renamed project sample_project to renamed\n"
    assert cli("phub projects list") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name", " renamed"]


def test_rename_unknown_project_fails(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub projects rename unknown renamed") == 1

    assert capsys.readouterr().err == "project unknown does not exist\n"


def test_delete_project(cli, given, capsys: pytest.CaptureFixture[str]):
    given("phub projects create sample_project")

    assert cli("phub projects delete sample_project") == 0

    assert capsys.readouterr().out == "deleted project sample_project\n"
    assert cli("phub projects list") == 0
    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name"]


def test_delete_unknown_project_fails(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub projects delete unknown") == 1

    assert capsys.readouterr().err == "project unknown does not exist\n"
