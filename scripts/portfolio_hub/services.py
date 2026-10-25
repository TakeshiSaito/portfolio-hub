from collections.abc import Iterable, Sequence

from dependency_injector.wiring import Provide, inject

from portfolio_hub.environment import TERMINAL, Environment, EnvironmentAlreadyExistsError, EnvironmentName, ToolName
from portfolio_hub.environment import Repository as EnvironmentRepository
from portfolio_hub.package import Package
from portfolio_hub.project import Project
from portfolio_hub.project import Repository as ProjectRepository


@inject
def delete_project(
    project: Project,
    *,
    project_repository: ProjectRepository = Provide["project_repository"],
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> list[Environment]:
    environments = environment_repository.list(project.id)
    for environment in environments:
        environment_repository.delete(environment.id)
    project_repository.delete(project.id)
    return environments


@inject
def create_environment(
    project: Project,
    name: EnvironmentName,
    packages: Iterable[Package],
    tools: Iterable[ToolName] = (),
    default_tool: ToolName = TERMINAL,
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> Environment:
    environment = Environment(project.id, name, packages, tools, default_tool)
    create_environments(project, [environment], environment_repository=environment_repository)
    return environment


@inject
def create_environments(
    project: Project,
    environments: Sequence[Environment],
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> None:
    environments_in_project = environment_repository.list(project.id)
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
def rename_environment(
    environment: Environment,
    name: EnvironmentName,
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
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
