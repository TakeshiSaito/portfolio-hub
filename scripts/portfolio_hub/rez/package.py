import builtins
from pathlib import Path

from rez.config import config
from rez.packages import iter_package_families

from portfolio_hub.package import Package, PackageName, PackageVersion, Repository


class RezPackageRepository(Repository):

    def __init__(self, bundled_packages_path: Path) -> None:
        self._bundled_packages_path = bundled_packages_path

    def list(self) -> builtins.list[Package]:
        paths = list(dict.fromkeys([*config.packages_path, str(self._bundled_packages_path)]))
        return [
            Package(PackageName(package.name), PackageVersion(str(package.version)))
            for family in iter_package_families(paths=paths)
            for package in family.iter_packages()
        ]
