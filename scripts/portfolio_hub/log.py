import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from portfolio_hub.env import Env


class LogEnv(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PORTFOLIO_HUB_LOG_", env_file=".env", extra="ignore")

    path: Path = Field(default_factory=lambda: Env().home / "logs" / "portfolio_hub.log")


def configure(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("portfolio_hub")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    handler = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
