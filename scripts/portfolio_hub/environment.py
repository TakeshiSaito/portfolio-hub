import builtins
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import Annotated
from uuid import UUID, uuid4

from dependency_injector.wiring import Provide, inject
from pydantic import Field, RootModel

from portfolio_hub.package import Package


class EnvironmentNotFoundError(LookupError):
    pass


class EnvironmentAlreadyExistsError(ValueError):
    pass


class ToolNotRegisteredError(ValueError):
    pass


class EnvironmentName(RootModel[Annotated[str, Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_]+$")]], frozen=True):

    def __str__(self) -> str:
        return self.root


class ToolName(RootModel[Annotated[str, Field(pattern=r"^\S{1,64}$")]], frozen=True):

    def __str__(self) -> str:
        return self.root


TERMINAL = ToolName("terminal")


class Environment:

    def __init__(
        self,
        project_id: UUID,
        name: EnvironmentName,
        packages: Iterable[Package],
        tools: Iterable[ToolName] = (),
        default_tool: ToolName = TERMINAL,
        id: UUID | None = None,
    ) -> None:
        self._id = id or uuid4()
        self._project_id = project_id
        self._name = name
        self._packages = self._validated_packages(packages)
        self._tools, self._default_tool = self._validated_tools(tools, default_tool)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Environment) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self._id)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def project_id(self) -> UUID:
        return self._project_id

    @property
    def name(self) -> EnvironmentName:
        return self._name

    @property
    def packages(self) -> tuple[Package, ...]:
        return self._packages

    @property
    def tools(self) -> tuple[ToolName, ...]:
        return self._tools

    @property
    def default_tool(self) -> ToolName:
        return self._default_tool

    def rename(self, name: EnvironmentName) -> None:
        self._name = name

    def replace_packages(self, packages: Iterable[Package]) -> None:
        self._packages = self._validated_packages(packages)

    def replace_tools(self, tools: Iterable[ToolName], default_tool: ToolName = TERMINAL) -> None:
        self._tools, self._default_tool = self._validated_tools(tools, default_tool)

    def tool_to_launch(self, tool: ToolName | None = None) -> ToolName:
        tool = self._default_tool if tool is None else tool
        if tool != TERMINAL and tool not in self._tools:
            raise ToolNotRegisteredError(f"tool {tool} is not one of the tools of environment {self._name}")
        return tool

    def _validated_packages(self, packages: Iterable[Package]) -> tuple[Package, ...]:
        packages = tuple(packages)
        if not packages:
            raise ValueError("an environment needs at least one package")
        if duplicates := self._duplicates([str(package.name) for package in packages]):
            raise ValueError(f"packages are chosen more than once: {', '.join(duplicates)}")
        return packages

    def _validated_tools(self, tools: Iterable[ToolName], default_tool: ToolName) -> tuple[tuple[ToolName, ...], ToolName]:
        tools = tuple(tools)
        if duplicates := self._duplicates([str(tool) for tool in tools]):
            raise ValueError(f"tools are registered more than once: {', '.join(duplicates)}")
        if default_tool != TERMINAL and default_tool not in tools:
            raise ValueError(f"default tool {default_tool} is not one of the tools")
        return tools, default_tool

    def _duplicates(self, values: Sequence[str]) -> list[str]:
        return sorted({value for value in values if values.count(value) > 1})


class Repository(ABC):

    @abstractmethod
    def get(self, environment_id: UUID) -> Environment:
        ...

    @abstractmethod
    def list(self, project_id: UUID) -> builtins.list[Environment]:
        ...

    @abstractmethod
    def save(self, environment: Environment) -> None:
        ...

    @abstractmethod
    def delete(self, environment_id: UUID) -> None:
        ...


@inject
def create(
    project_id: UUID,
    name: EnvironmentName,
    packages: Iterable[Package],
    tools: Iterable[ToolName] = (),
    default_tool: ToolName = TERMINAL,
    *,
    environment_repository: Repository = Provide["environment_repository"],
) -> Environment:

    environment = Environment(project_id, name, packages, tools, default_tool)
    check_names(project_id, [environment], environment_repository=environment_repository)

    return environment


@inject
def check_names(
    project_id: UUID,
    environments: Sequence[Environment],
    *,
    environment_repository: Repository = Provide["environment_repository"],
) -> None:
    environments_in_project = environment_repository.list(project_id)
    for environment in environments:
        name_is_in_project = False
        for existing in environments_in_project:
            if existing.name == environment.name:
                name_is_in_project = True
                break
        if name_is_in_project:
            raise EnvironmentAlreadyExistsError(f"the project already has an environment named {environment.name}")
        environments_in_project.append(environment)


@inject
def rename(
    environment: Environment,
    name: EnvironmentName,
    *,
    environment_repository: Repository = Provide["environment_repository"],
) -> None:
    environments_in_project = environment_repository.list(environment.project_id)
    name_is_in_project = False
    for saved_environment in environments_in_project:
        if saved_environment.id == environment.id:
            continue
        if saved_environment.name == name:
            name_is_in_project = True
            break
    if name_is_in_project:
        raise EnvironmentAlreadyExistsError(f"the project already has an environment named {name}")
    environment.rename(name)
