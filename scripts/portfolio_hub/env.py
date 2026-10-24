from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PORTFOLIO_HUB_", env_file=".env", extra="ignore")
    host: str = "127.0.0.1"
    port: int = 8000
    home: Path = Path(__file__).parents[2]
