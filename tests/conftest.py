import tomllib
from collections.abc import Iterator
from pathlib import Path

import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto
from portfolio_hub.installer import Container

PACKAGES = Path(__file__).parents[1] / "packages"
TERMINAL = Path(__file__).parent / "terminal" / "fake_terminal"


@pytest.fixture(autouse=True)
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Container]:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REZ_PACKAGES_PATH", str(PACKAGES))
    monkeypatch.setenv("PORTFOLIO_HUB_HOME", str(tmp_path))
    monkeypatch.setenv("PORTFOLIO_HUB_REZ_TERMINAL_COMMAND", str(TERMINAL))
    container = Container()
    container.database()
    yield container
    container.unwire()


@pytest.fixture
def database(tmp_path: Path) -> Path:
    return tmp_path / "portfolio_hub.db"


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    return tmp_path / "logs" / "portfolio_hub.log"


@pytest.fixture
def project_metadata() -> dict[str, str]:
    return tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8"))["project"]


@pytest.fixture
def project() -> dto.Project:
    return applications.create_project("sample_project")
