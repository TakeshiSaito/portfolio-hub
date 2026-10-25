import os
import shlex
from pathlib import Path
from subprocess import Popen
from tempfile import NamedTemporaryFile
from threading import Thread

from rez.config import config
from rez.exceptions import PackageFamilyNotFoundError, PackageNotFoundError
from rez.resolved_context import ResolvedContext

from portfolio_hub.environment import TERMINAL, Environment, ToolName
from portfolio_hub.launcher import FailedToResolveError, Launcher, LaunchResult
from portfolio_hub.package import Package, PackageName, PackageVersion


class RezLauncher(Launcher):

    def __init__(self, bundled_packages_path: Path, terminal_command: str) -> None:
        self._bundled_packages_path = bundled_packages_path
        self._terminal_command = shlex.split(terminal_command)

    def resolve(self, environment: Environment) -> list[Package]:
        return self._resolved_packages(self._resolve_context(environment))

    def run(self, environment: Environment, tool: ToolName) -> LaunchResult:
        context = self._resolve_context(environment)
        process = self._open_terminal(context) if tool == TERMINAL else context.execute_command([str(tool)], parent_environ=dict(os.environ), start_new_session=True)
        Thread(target=process.wait, daemon=True).start()
        return LaunchResult(tool=tool, resolved_packages=tuple(self._resolved_packages(context)), pid=process.pid)

    def _resolve_context(self, environment: Environment) -> ResolvedContext:
        paths = list(dict.fromkeys([*config.packages_path, str(self._bundled_packages_path)]))
        try:
            context = ResolvedContext([f"{package.name}-{package.version}" for package in environment.packages], package_paths=paths)
        except (PackageNotFoundError, PackageFamilyNotFoundError) as error:
            raise FailedToResolveError(str(error)) from error
        if not context.success:
            raise FailedToResolveError(context.failure_description)
        return context

    def _resolved_packages(self, context: ResolvedContext) -> list[Package]:
        return [Package(PackageName(variant.name), PackageVersion(str(variant.version))) for variant in context.resolved_packages or []]

    def _open_terminal(self, context: ResolvedContext) -> Popen:
        with NamedTemporaryFile("w", suffix=".command", delete=False) as script:
            script.write("#!/bin/bash\n")
            script.write('rm -f -- "$0"\n')
            script.write(context.get_shell_code(shell="bash"))
            script.write('\nexec "${SHELL:-/bin/bash}" -i\n')
        Path(script.name).chmod(0o755)
        return Popen([*self._terminal_command, script.name], start_new_session=True)
