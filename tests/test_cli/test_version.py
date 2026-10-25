import pytest


def test_version(cli, capsys: pytest.CaptureFixture[str], version: str):
    with pytest.raises(SystemExit) as exit:
        cli("phub --version")

    assert exit.value.code == 0
    assert capsys.readouterr().out == f"phub {version}\n"
