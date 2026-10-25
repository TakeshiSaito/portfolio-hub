import builtins
from abc import ABC, abstractmethod
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import Field, RootModel


class ProjectNotFoundError(LookupError):
    pass


class ProjectAlreadyExistsError(ValueError):
    pass


class ProjectName(RootModel[Annotated[str, Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_]+$")]], frozen=True):

    def __str__(self) -> str:
        return self.root


class Project:

    def __init__(self, name: ProjectName, id: UUID | None = None) -> None:
        self._id = id or uuid4()
        self._name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Project) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self._id)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> ProjectName:
        return self._name

    def rename(self, name: ProjectName) -> None:
        self._name = name


class Repository(ABC):

    @abstractmethod
    def get(self, project_id: UUID) -> Project:
        ...

    @abstractmethod
    def exists(self, project_id: UUID) -> bool:
        ...

    @abstractmethod
    def list(self) -> builtins.list[Project]:
        ...

    @abstractmethod
    def save(self, project: Project) -> None:
        ...

    @abstractmethod
    def delete(self, project_id: UUID) -> None:
        ...
