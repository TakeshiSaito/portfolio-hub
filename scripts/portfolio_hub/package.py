import builtins
from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import Field, RootModel


class PackageName(RootModel[Annotated[str, Field(pattern=r"^[A-Za-z0-9_][A-Za-z0-9_.]*$")]], frozen=True):

    def __str__(self) -> str:
        return self.root


class PackageVersion(RootModel[Annotated[str, Field(min_length=1)]], frozen=True):

    def __str__(self) -> str:
        return self.root


class Package:

    def __init__(self, name: PackageName, version: PackageVersion) -> None:
        self._name = name
        self._version = version

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Package) and (other.name, other.version) == (self.name, self.version)

    def __hash__(self) -> int:
        return hash((self._name, self._version))

    @property
    def name(self) -> PackageName:
        return self._name

    @property
    def version(self) -> PackageVersion:
        return self._version


class Repository(ABC):

    @abstractmethod
    def list(self) -> builtins.list[Package]:
        ...
