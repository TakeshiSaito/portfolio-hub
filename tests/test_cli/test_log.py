import re
from pathlib import Path


def test_create_project_writes_the_log_to_the_file(cli, log_file: Path):
    assert cli("phub projects create foo") == 0

    [line] = log_file.read_text().splitlines()
    _, message = line.split(" ", 1)
    assert re.fullmatch(r"INFO portfolio_hub\.applications created project foo \([0-9a-f-]{36}\)", message)
