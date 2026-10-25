from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.pool import NullPool

from portfolio_hub.env import Env
from portfolio_hub.sqlite.models import Base


class SqLiteEnv(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PORTFOLIO_HUB_SQLITE_", env_file=".env", extra="ignore")

    path: Path = Field(default_factory=lambda: Env().home / "portfolio_hub.db")


def connect(path: Path) -> Engine:
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}", poolclass=NullPool)
    event.listen(engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys = ON"))
    Base.metadata.create_all(engine)
    return engine
