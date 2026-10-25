from pathlib import Path

import pytest


def test_start_without_a_database_creates_the_sample(cli, database: Path, capsys: pytest.CaptureFixture[str]):
    database.unlink()

    assert cli("phub environments list sample_project") == 0

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [
        " name                packages     tools  default tool",
        " sample_environment  hello 1.0.0  hello  terminal",
    ]


def test_start_with_an_existing_database_does_not_create_the_sample(cli, capsys: pytest.CaptureFixture[str]):
    assert cli("phub projects list") == 0

    assert [line.rstrip() for line in capsys.readouterr().out.splitlines()] == [" name"]
