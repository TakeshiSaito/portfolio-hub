# Changelog

## [0.0.2] - 2026-10-25

### Changed

- Support only Python 3.14 (`requires-python = ">=3.14,<3.15"`), because rez cannot load its plugins on Python 3.15.

## [0.0.1] - 2026-10-25

### Added

- First release: a hub that manages projects and their rez environments on one machine and launches tools in them.
- Create, rename and delete projects and environments, replace the packages and tools of an environment, resolve its packages, and launch tools (`terminal` opens a terminal).
- A command line (`phub`) and an HTTP API (FastAPI, `phub serve`). `phub --version` and Swagger UI show the version.
- Data is stored in SQLite, and every operation that changes it is logged.
