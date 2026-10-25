import argparse
import sys
from uuid import UUID

from rich.console import Console
from rich.table import Table

from portfolio_hub import __version__, applications, http, installer
from portfolio_hub.applications import dto
from portfolio_hub.environment import TERMINAL, EnvironmentNotFoundError
from portfolio_hub.launcher import FailedToResolveError
from portfolio_hub.project import ProjectNotFoundError


def main(argv: list[str] | None = None) -> int:
    installer.get()
    arguments = _parser().parse_args(sys.argv[1:] if argv is None else argv)
    try:
        arguments.handler(arguments)
    except (LookupError, ValueError, FailedToResolveError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phub", description="Manage projects and their rez environments, and launch tools in them.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(title="commands", metavar="COMMAND", required=True)

    projects = commands.add_parser("projects", help="list, create, rename or delete projects")
    project_commands = projects.add_subparsers(title="commands", metavar="COMMAND", required=True)

    list_projects = project_commands.add_parser("list", help="list the projects")
    list_projects.set_defaults(handler=_list_projects)

    create_project = project_commands.add_parser("create", help="create a project")
    create_project.add_argument("name", help="name of the new project")
    create_project.set_defaults(handler=_create_project)

    rename_project = project_commands.add_parser("rename", help="rename a project")
    rename_project.add_argument("name", help="name of the project")
    rename_project.add_argument("new_name", help="new name of the project")
    rename_project.set_defaults(handler=_rename_project)

    delete_project = project_commands.add_parser("delete", help="delete a project and its environments")
    delete_project.add_argument("name", help="name of the project")
    delete_project.set_defaults(handler=_delete_project)

    environments = commands.add_parser("environments", help="list, create, change or delete the environments of a project")
    environment_commands = environments.add_subparsers(title="commands", metavar="COMMAND", required=True)

    list_environments = environment_commands.add_parser("list", help="list the environments of a project with their packages and tools")
    list_environments.add_argument("project", help="name of the project")
    list_environments.set_defaults(handler=_list_environments)

    create_environment = environment_commands.add_parser("create", help="create an environment in a project")
    create_environment.add_argument("project", help="name of the project")
    create_environment.add_argument("name", help="name of the new environment")
    create_environment.add_argument("--package", nargs=2, action="append", default=[], metavar=("NAME", "VERSION"), help="a package of the environment; repeat for more")
    create_environment.add_argument("--tool", action="append", default=[], help="a tool of the environment; repeat for more")
    create_environment.add_argument("--default-tool", default=str(TERMINAL), help="the tool launched when none is given; one of --tool, or terminal (the default)")
    create_environment.set_defaults(handler=_create_environment)

    rename_environment = environment_commands.add_parser("rename", help="rename an environment")
    _add_environment_arguments(rename_environment)
    rename_environment.add_argument("new_name", help="new name of the environment")
    rename_environment.set_defaults(handler=_rename_environment)

    set_packages = environment_commands.add_parser("set-packages", help="replace the packages of an environment")
    _add_environment_arguments(set_packages)
    set_packages.add_argument("--package", nargs=2, action="append", default=[], metavar=("NAME", "VERSION"), help="a package of the environment; repeat for more")
    set_packages.set_defaults(handler=_set_packages)

    set_tools = environment_commands.add_parser("set-tools", help="replace the tools of an environment")
    _add_environment_arguments(set_tools)
    set_tools.add_argument("--tool", action="append", default=[], help="a tool of the environment; repeat for more, omit for none")
    set_tools.add_argument("--default-tool", default=str(TERMINAL), help="the tool launched when none is given; one of --tool, or terminal (the default)")
    set_tools.set_defaults(handler=_set_tools)

    delete_environment = environment_commands.add_parser("delete", help="delete an environment")
    _add_environment_arguments(delete_environment)
    delete_environment.set_defaults(handler=_delete_environment)

    packages = commands.add_parser("packages", help="list the packages that environments can use")
    packages.set_defaults(handler=_list_packages)

    resolve = commands.add_parser("resolve", help="show the packages an environment resolves to, without launching it")
    _add_environment_arguments(resolve)
    resolve.set_defaults(handler=_resolve)

    launch = commands.add_parser("launch", help="launch a tool in an environment; the tool terminal opens a terminal in it")
    _add_environment_arguments(launch)
    launch.add_argument("tool", nargs="?", help="omit to launch the default tool of the environment")
    launch.set_defaults(handler=_launch)

    serve = commands.add_parser("serve", help="start the HTTP API on this machine (PORTFOLIO_HUB_HOST and PORTFOLIO_HUB_PORT, 127.0.0.1:8000 by default)")
    serve.set_defaults(handler=_serve)

    return parser


def _add_environment_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("project", help="name of the project")
    parser.add_argument("environment", help="name of the environment")


def _list_projects(arguments: argparse.Namespace) -> None:
    for project in applications.list_projects():
        print(project.name)


def _create_project(arguments: argparse.Namespace) -> None:
    applications.create_project(arguments.name)


def _rename_project(arguments: argparse.Namespace) -> None:
    applications.rename_project(_get_project_id(arguments.name), arguments.new_name)


def _delete_project(arguments: argparse.Namespace) -> None:
    applications.delete_project(_get_project_id(arguments.name))


def _list_environments(arguments: argparse.Namespace) -> None:
    project_id = _get_project_id(arguments.project)
    table = Table("name", "packages", "tools", "default tool", box=None)
    for environment in applications.list_environments():
        if environment.project_id == project_id:
            packages = sorted(environment.packages, key=lambda package: (package.name, package.version))
            table.add_row(
                environment.name,
                ", ".join(f"{package.name} {package.version}" for package in packages),
                ", ".join(sorted(environment.tools)),
                environment.default_tool,
            )
    Console().print(table)


def _create_environment(arguments: argparse.Namespace) -> None:
    packages = [(name, version) for name, version in arguments.package]
    applications.create_environment(_get_project_id(arguments.project), arguments.name, packages, arguments.tool, arguments.default_tool)


def _rename_environment(arguments: argparse.Namespace) -> None:
    environment = _get_environment(arguments.project, arguments.environment)
    applications.rename_environment(environment.id, arguments.new_name)


def _set_packages(arguments: argparse.Namespace) -> None:
    environment = _get_environment(arguments.project, arguments.environment)
    packages = [(name, version) for name, version in arguments.package]
    applications.replace_packages(environment.id, packages)


def _set_tools(arguments: argparse.Namespace) -> None:
    environment = _get_environment(arguments.project, arguments.environment)
    applications.replace_tools(environment.id, arguments.tool, arguments.default_tool)


def _delete_environment(arguments: argparse.Namespace) -> None:
    environment = _get_environment(arguments.project, arguments.environment)
    applications.delete_environment(environment.id)


def _list_packages(arguments: argparse.Namespace) -> None:
    _print_packages(applications.list_packages())


def _resolve(arguments: argparse.Namespace) -> None:
    environment = _get_environment(arguments.project, arguments.environment)
    _print_packages(applications.resolve_environment(environment.id))


def _launch(arguments: argparse.Namespace) -> None:
    environment = _get_environment(arguments.project, arguments.environment)
    print(applications.launch(environment.id, arguments.tool).pid)


def _serve(arguments: argparse.Namespace) -> None:
    http.serve()


def _print_packages(packages: list[dto.Package]) -> None:
    table = Table("name", "version", box=None)
    for package in sorted(packages, key=lambda package: (package.name, package.version)):
        table.add_row(package.name, package.version)
    Console().print(table)


def _get_project_id(name: str) -> UUID:
    for project in applications.list_projects():
        if project.name == name:
            return project.id
    raise ProjectNotFoundError(f"project {name} does not exist")


def _get_environment(project: str, name: str) -> dto.Environment:
    project_id = _get_project_id(project)
    for environment in applications.list_environments():
        if environment.project_id == project_id and environment.name == name:
            return environment
    raise EnvironmentNotFoundError(f"environment {name} does not exist in project {project}")
