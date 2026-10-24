from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class Environment(Base):
    __tablename__ = "environments"
    __table_args__ = (UniqueConstraint("project_id", "name"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="RESTRICT"))
    name: Mapped[str]
    default_tool: Mapped[str]
    packages: Mapped[list[EnvironmentPackage]] = relationship(cascade="all, delete-orphan")
    tools: Mapped[list[EnvironmentTool]] = relationship(cascade="all, delete-orphan")


class EnvironmentPackage(Base):
    __tablename__ = "environment_packages"

    environment_id: Mapped[UUID] = mapped_column(ForeignKey("environments.id", ondelete="CASCADE"), primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str]


class EnvironmentTool(Base):
    __tablename__ = "environment_tools"

    environment_id: Mapped[UUID] = mapped_column(ForeignKey("environments.id", ondelete="CASCADE"), primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
