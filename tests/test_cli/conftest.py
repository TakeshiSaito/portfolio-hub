import shlex
from collections.abc import Callable

import pytest

from portfolio_hub.cli import main

type Cli = Callable[[str], int]


@pytest.fixture
def cli() -> Cli:
    def run(command: str) -> int:
        _, *arguments = shlex.split(command)
        return main(arguments)

    return run
