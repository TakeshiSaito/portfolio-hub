import re

import pytest


@pytest.mark.parametrize(
    ("command", "subcommands"),
    [
        ("phub --help", ["projects", "environments", "packages", "resolve", "launch", "serve"]),
        ("phub projects --help", ["list", "create", "rename", "delete"]),
        ("phub environments --help", ["list", "create", "rename", "set-packages", "set-tools", "delete"]),
    ],
    ids=["top", "projects", "environments"],
)
def test_help_lists_every_command(cli, capsys: pytest.CaptureFixture[str], command: str, subcommands: list[str]):
    with pytest.raises(SystemExit) as exit:
        cli(command)

    assert exit.value.code == 0
    out = capsys.readouterr().out
    for subcommand in subcommands:
        assert re.search(rf"^\s+{subcommand}\s+\S", out, re.MULTILINE), subcommand
