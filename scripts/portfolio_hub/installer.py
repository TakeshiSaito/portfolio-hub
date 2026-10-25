from dependency_injector import containers, providers

from portfolio_hub import applications, log
from portfolio_hub.rez import RezEnv
from portfolio_hub.rez.launcher import RezLauncher
from portfolio_hub.rez.package import RezPackageRepository
from portfolio_hub.sqlite import SqLiteEnv, connect
from portfolio_hub.sqlite.environment import SqLiteEnvironmentRepository
from portfolio_hub.sqlite.project import SqLiteProjectRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["portfolio_hub.applications", "portfolio_hub.services"])

    rez_env = providers.Singleton(RezEnv)
    sqlite_env = providers.Singleton(SqLiteEnv)
    database = providers.Singleton(connect, sqlite_env.provided.path)
    project_repository = providers.Singleton(SqLiteProjectRepository, database)
    environment_repository = providers.Singleton(SqLiteEnvironmentRepository, database)
    package_repository = providers.Singleton(RezPackageRepository, rez_env.provided.bundled_packages_path)
    launcher = providers.Singleton(RezLauncher, rez_env.provided.bundled_packages_path, rez_env.provided.terminal_command)


def get() -> Container:
    log.configure(log.LogEnv().path)
    is_new = not SqLiteEnv().path.exists()
    container = Container()
    if is_new:
        applications.create_sample()
    return container
