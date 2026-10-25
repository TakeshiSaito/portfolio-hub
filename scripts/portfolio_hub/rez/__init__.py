import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RezEnv(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PORTFOLIO_HUB_REZ_", env_file=".env", extra="ignore")

    bundled_packages_path: Path = Path(__file__).parents[3] / "packages"
    terminal_command: str = Field(default_factory=lambda: "open -a Terminal" if sys.platform == "darwin" else "x-terminal-emulator -e")
