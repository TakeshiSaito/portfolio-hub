from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, PositiveInt

from portfolio_hub.environment import Environment, ToolName
from portfolio_hub.package import Package


class FailedToResolveError(RuntimeError):
    pass


class LaunchResult(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    resolved_packages: tuple[Package, ...]
    pid: PositiveInt


class Launcher(ABC):

    @abstractmethod
    def resolve(self, environment: Environment) -> list[Package]:
        ...

    @abstractmethod
    def run(self, environment: Environment, tool: ToolName) -> LaunchResult:
        ...
