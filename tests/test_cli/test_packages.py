import pytest


def test_list_packages(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub packages") == 0

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name            version",
        " greeter         1.0.0",
        " greeter         2.0.0",
        " greeter_plugin  1.0.0",
        " hello           1.0.0",
    ]
