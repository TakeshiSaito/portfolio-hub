from typing import Self
from uuid import UUID

from pydantic import BaseModel

from portfolio_hub import environment, launcher, package, project


class Project(BaseModel, frozen=True):
    id: UUID
    name: str

    @classmethod
    def from_project(cls, entity: project.Project) -> Self:
        return cls(id=entity.id, name=str(entity.name))


class Package(BaseModel, frozen=True):
    name: str
    version: str

    @classmethod
    def from_package(cls, entity: package.Package) -> Self:
        return cls(name=str(entity.name), version=str(entity.version))


class NewEnvironment(BaseModel, frozen=True):
    name: str
    packages: tuple[Package, ...]
    tools: tuple[str, ...] = ()
    default_tool: str = str(environment.TERMINAL)


class Environment(BaseModel, frozen=True):
    id: UUID
    project_id: UUID
    name: str
    packages: tuple[Package, ...]
    tools: tuple[str, ...]
    default_tool: str

    @classmethod
    def from_environment(cls, entity: environment.Environment) -> Self:
        return cls(
            id=entity.id,
            project_id=entity.project_id,
            name=str(entity.name),
            packages=tuple(Package.from_package(item) for item in entity.packages),
            tools=tuple(str(tool) for tool in entity.tools),
            default_tool=str(entity.default_tool),
        )


class Launch(BaseModel, frozen=True):
    pid: int
    resolved_packages: tuple[Package, ...]

    @classmethod
    def from_result(cls, result: launcher.LaunchResult) -> Self:
        return cls(pid=result.pid, resolved_packages=tuple(Package.from_package(item) for item in result.resolved_packages))
