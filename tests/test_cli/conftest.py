import shlex
from collections.abc import Callable

import pytest

from portfolio_hub.cli import main

type Cli = Callable[[str], int]
type Given = Callable[[str], None]


@pytest.fixture
def cli() -> Cli:
    def run(command: str) -> int:
        _, *arguments = shlex.split(command)
        return main(arguments)

    return run


@pytest.fixture
def given(cli: Cli, capsys: pytest.CaptureFixture[str]) -> Given:
    def run(command: str) -> None:
        assert cli(command) == 0
        capsys.readouterr()

    return run
