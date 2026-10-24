import builtins
from uuid import UUID

from sqlalchemy import Engine, literal_column, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from portfolio_hub.project import Project, ProjectAlreadyExistsError, ProjectName, ProjectNotFoundError, Repository
from portfolio_hub.sqlite import models


class SqLiteProjectRepository(Repository):

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get(self, project_id: UUID) -> Project:
        with Session(self._engine) as session:
            record = session.get(models.Project, project_id)
            if record is None:
                raise ProjectNotFoundError(f"project {project_id} does not exist")
            return Project(ProjectName(record.name), id=record.id)

    def exists(self, project_id: UUID) -> bool:
        with Session(self._engine) as session:
            return session.get(models.Project, project_id) is not None

    def list(self) -> builtins.list[Project]:
        with Session(self._engine) as session:
            records = session.scalars(select(models.Project).order_by(literal_column("rowid")))
            return [Project(ProjectName(record.name), id=record.id) for record in records]

    def save(self, project: Project) -> None:
        with Session(self._engine) as session:
            session.merge(models.Project(id=project.id, name=str(project.name)))
            try:
                session.commit()
            except IntegrityError as error:
                raise ProjectAlreadyExistsError(f"project {project.name} already exists") from error

    def delete(self, project_id: UUID) -> None:
        with Session(self._engine) as session:
            record = session.get(models.Project, project_id)
            if record is None:
                raise ProjectNotFoundError(f"project {project_id} does not exist")
            session.delete(record)
            session.commit()
