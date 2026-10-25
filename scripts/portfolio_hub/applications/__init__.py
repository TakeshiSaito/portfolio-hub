import logging
from collections.abc import Sequence
from uuid import UUID

from dependency_injector.wiring import Provide, inject

from portfolio_hub import services
from portfolio_hub.applications import dto
from portfolio_hub.environment import TERMINAL, Environment, EnvironmentName, ToolName, ToolNotRegisteredError
from portfolio_hub.environment import Repository as EnvironmentRepository
from portfolio_hub.launcher import Launcher
from portfolio_hub.package import Package, PackageName, PackageVersion
from portfolio_hub.package import Repository as PackageRepository
from portfolio_hub.project import Project, ProjectName
from portfolio_hub.project import Repository as ProjectRepository

logger = logging.getLogger(__name__)


@inject
def list_projects(
    *,
    project_repository: ProjectRepository = Provide["project_repository"],
) -> list[dto.Project]:
    projects = project_repository.list()
    return [dto.Project.from_project(project) for project in projects]


@inject
def create_project(
    name: str,
    environments: Sequence[dto.NewEnvironment] = (),
    *,
    project_repository: ProjectRepository = Provide["project_repository"],
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> dto.Project:
    project = Project(ProjectName(name))

    created: list[Environment] = []
    for environment in environments:
        packages = [Package(PackageName(package.name), PackageVersion(package.version)) for package in environment.packages]
        tools = [ToolName(tool) for tool in environment.tools]
        created.append(Environment(project.id, EnvironmentName(environment.name), packages, tools, ToolName(environment.default_tool)))

    services.create_environments(project, created)
    project_repository.save(project)

    logger.info("created project %s (%s)", project.name, project.id)

    for environment in created:
        environment_repository.save(environment)
        logger.info("created environment %s (%s) in project %s", environment.name, environment.id, project.name)

    return dto.Project.from_project(project)


@inject
def rename_project(
    project_id: UUID,
    name: str,
    *,
    project_repository: ProjectRepository = Provide["project_repository"],
) -> None:
    project = project_repository.get(project_id)
    old_name = project.name
    project.rename(ProjectName(name))
    project_repository.save(project)
    logger.info("renamed project %s to %s (%s)", old_name, project.name, project.id)


@inject
def delete_project(
    project_id: UUID,
    *,
    project_repository: ProjectRepository = Provide["project_repository"],
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> None:
    project = project_repository.get(project_id)
    for environment in environment_repository.list(project_id):
        environment_repository.delete(environment.id)
        logger.info("deleted environment %s (%s)", environment.name, environment.id)
    project_repository.delete(project_id)
    logger.info("deleted project %s (%s)", project.name, project.id)


@inject
def list_environments(
    project_id: UUID,
    *,
    project_repository: ProjectRepository = Provide["project_repository"],
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> list[dto.Environment]:
    project = project_repository.get(project_id)
    environments = environment_repository.list(project.id)
    return [dto.Environment.from_environment(environment) for environment in environments]


@inject
def create_environment(
    project_id: UUID,
    name: str,
    packages: Sequence[tuple[str, str]],
    tools: Sequence[str] = (),
    default_tool: str = str(TERMINAL),
    *,
    project_repository: ProjectRepository = Provide["project_repository"],
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> dto.Environment:
    project = project_repository.get(project_id)
    environment = services.create_environment(
        project,
        EnvironmentName(name),
        [Package(PackageName(package_name), PackageVersion(version)) for package_name, version in packages],
        [ToolName(tool) for tool in tools],
        ToolName(default_tool),
    )
    environment_repository.save(environment)
    logger.info("created environment %s (%s) in project %s", environment.name, environment.id, project.name)
    return dto.Environment.from_environment(environment)


@inject
def rename_environment(
    environment_id: UUID,
    name: str,
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> None:
    environment = environment_repository.get(environment_id)
    old_name = environment.name
    services.rename_environment(environment, EnvironmentName(name))
    environment_repository.save(environment)
    logger.info("renamed environment %s to %s (%s)", old_name, environment.name, environment.id)


@inject
def replace_packages(
    environment_id: UUID,
    packages: Sequence[tuple[str, str]],
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> None:
    environment = environment_repository.get(environment_id)
    environment.replace_packages([Package(PackageName(name), PackageVersion(version)) for name, version in packages])
    environment_repository.save(environment)
    logger.info(
        "replaced the packages of environment %s (%s) with %s",
        environment.name,
        environment.id,
        ", ".join(f"{package.name} {package.version}" for package in environment.packages),
    )


@inject
def replace_tools(
    environment_id: UUID,
    tools: Sequence[str],
    default_tool: str = str(TERMINAL),
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> None:
    environment = environment_repository.get(environment_id)
    environment.replace_tools([ToolName(tool) for tool in tools], ToolName(default_tool))
    environment_repository.save(environment)
    logger.info(
        "replaced the tools of environment %s (%s) with %s; default tool %s",
        environment.name,
        environment.id,
        ", ".join(str(tool) for tool in environment.tools),
        environment.default_tool,
    )


@inject
def delete_environment(
    environment_id: UUID,
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
) -> None:
    environment = environment_repository.get(environment_id)
    environment_repository.delete(environment_id)
    logger.info("deleted environment %s (%s)", environment.name, environment.id)


@inject
def list_packages(
    *,
    package_repository: PackageRepository = Provide["package_repository"],
) -> list[dto.Package]:
    packages = package_repository.list()
    return [dto.Package.from_package(package) for package in packages]


@inject
def resolve_environment(
    environment_id: UUID,
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
    launcher: Launcher = Provide["launcher"],
) -> list[dto.Package]:
    environment = environment_repository.get(environment_id)
    packages = launcher.resolve(environment)
    return [dto.Package.from_package(package) for package in packages]


@inject
def launch(
    environment_id: UUID,
    tool: str | None = None,
    *,
    environment_repository: EnvironmentRepository = Provide["environment_repository"],
    launcher: Launcher = Provide["launcher"],
) -> dto.Launch:
    environment = environment_repository.get(environment_id)
    tool_name = environment.default_tool if tool is None else ToolName(tool)

    if not environment.can_launch(tool_name):
        raise ToolNotRegisteredError(f"tool {tool_name} is not one of the tools of environment {environment.name}")

    result = launcher.run(environment, tool_name)
    logger.info("launched %s in environment %s (%s) with pid %s", tool_name, environment.name, environment.id, result.pid)
    return dto.Launch.from_result(result)


def create_sample() -> None:
    create_project(
        "sample_project",
        environments=[
            dto.NewEnvironment(name="sample_environment", packages=[dto.Package(name="hello", version="1.0.0")], tools=["hello"]),
        ],
    )
