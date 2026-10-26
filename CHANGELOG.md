# Changelog

## [0.0.3] - 2026-10-26

### Fixed

- Resolving or launching an environment uses the exact package version that was chosen. A later build, such as `2.0.0.1`, is no longer selected when the environment asks for `2.0.0`.

## [0.0.2] - 2026-10-25

### Added

- Commands that change data print one line about what they did, and `phub launch` prints the launched tool, the environment and the PID.
- The launch result names the tool that was launched, so a caller that omitted the tool can see which default tool ran.
- `phub --help` and Swagger UI show the project description. Swagger UI groups the operations into projects, environments, packages and launches, and lists the error responses of each operation.

### Changed

- Support only Python 3.14 (`requires-python = ">=3.14,<3.15"`), because rez cannot load its plugins on Python 3.15.
- `applications.list_environments` takes a project ID and lists only the environments of that project. It fails with `ProjectNotFoundError` when the project does not exist.
- Creating a project with two environments of the same name fails with the message `the project already has an environment named <name>`, the same as creating one environment with a name already in the project.
- `phub projects list` prints a table like the other lists, so an empty list still shows its header.
- The command line prints validation errors as their messages on one line, as the HTTP API does.
- The HTTP API answers an invalid request, such as a path with a malformed ID, with one `detail` message like the other validation errors.
- The log names the project or environment, not only its ID, when one is created or deleted.
- The sample environment opens a terminal when launched without a tool. Its `hello` tool stays registered.

### Removed

- Shell completion with argcomplete.

### Fixed

- Launching a tool that is not registered in the environment fails with `ToolNotRegisteredError` (422 in the HTTP API) instead of a traceback from rez.
- A package or version that does not exist is reported as a resolve failure (422 in the HTTP API) instead of an unhandled error.

## [0.0.1] - 2026-10-25

### Added

- First release: a hub that manages projects and their rez environments on one machine and launches tools in them.
- Create, rename and delete projects and environments, replace the packages and tools of an environment, resolve its packages, and launch tools (`terminal` opens a terminal).
- A command line (`phub`) and an HTTP API (FastAPI, `phub serve`). `phub --version` and Swagger UI show the version.
- Data is stored in SQLite, and every operation that changes it is logged.
