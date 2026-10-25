from pathlib import Path

from rez.config import config

from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_list_packages():
    assert set(applications.list_packages()) == {
        dto.Package(name="greeter", version="1.0.0"),
        dto.Package(name="greeter", version="2.0.0"),
        dto.Package(name="greeter_plugin", version="1.0.0"),
        dto.Package(name="hello", version="1.0.0"),
    }


def test_list_packages_includes_bundled_packages_when_they_are_not_on_the_search_path(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    config.override("packages_path", [str(empty)])
    try:
        assert list(config.packages_path) == [str(empty)]
        packages = applications.list_packages()
    finally:
        config.remove_override("packages_path")

    assert set(packages) == {
        dto.Package(name="greeter", version="1.0.0"),
        dto.Package(name="greeter", version="2.0.0"),
        dto.Package(name="greeter_plugin", version="1.0.0"),
        dto.Package(name="hello", version="1.0.0"),
    }
