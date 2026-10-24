from pathlib import Path

from portfolio_hub import applications


def test_create_project_writes_the_log_to_the_file(cli, log_file: Path):
    assert cli("phub projects create foo") == 0

    [project] = applications.list_projects()
    [line] = log_file.read_text().splitlines()
    _, message = line.split(" ", 1)
    assert message == f"INFO portfolio_hub.applications created project foo ({project.id})"
