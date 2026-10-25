import builtins
from uuid import UUID

from sqlalchemy import Engine, literal_column, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from portfolio_hub.environment import Environment, EnvironmentAlreadyExistsError, EnvironmentName, EnvironmentNotFoundError, Repository, ToolName
from portfolio_hub.package import Package, PackageName, PackageVersion
from portfolio_hub.sqlite import models


class SqLiteEnvironmentRepository(Repository):

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get(self, environment_id: UUID) -> Environment:
        with Session(self._engine) as session:
            record = session.get(models.Environment, environment_id)
            if record is None:
                raise EnvironmentNotFoundError(f"environment {environment_id} does not exist")
            return self._to_entity(record)

    def exists(self, environment_id: UUID) -> bool:
        with Session(self._engine) as session:
            return session.get(models.Environment, environment_id) is not None

    def list(self) -> builtins.list[Environment]:
        with Session(self._engine) as session:
            records = session.scalars(select(models.Environment).order_by(literal_column("rowid")))
            return [self._to_entity(record) for record in records]

    def save(self, environment: Environment) -> None:
        with Session(self._engine) as session:
            session.merge(self._to_record(environment))
            try:
                session.commit()
            except IntegrityError as error:
                if "UNIQUE constraint failed: environments" not in str(error.orig):
                    raise
                raise EnvironmentAlreadyExistsError(f"the project already has an environment named {environment.name}") from error

    def delete(self, environment_id: UUID) -> None:
        with Session(self._engine) as session:
            record = session.get(models.Environment, environment_id)
            if record is None:
                raise EnvironmentNotFoundError(f"environment {environment_id} does not exist")
            session.delete(record)
            session.commit()

    def _to_record(self, environment: Environment) -> models.Environment:
        return models.Environment(
            id=environment.id,
            project_id=environment.project_id,
            name=str(environment.name),
            default_tool=str(environment.default_tool),
            packages=[models.EnvironmentPackage(environment_id=environment.id, name=str(package.name), version=str(package.version)) for package in environment.packages],
            tools=[models.EnvironmentTool(environment_id=environment.id, name=str(tool)) for tool in environment.tools],
        )

    def _to_entity(self, record: models.Environment) -> Environment:
        return Environment(
            project_id=record.project_id,
            name=EnvironmentName(record.name),
            packages=[Package(PackageName(package.name), PackageVersion(package.version)) for package in record.packages],
            tools=[ToolName(tool.name) for tool in record.tools],
            default_tool=ToolName(record.default_tool),
            id=record.id,
        )
