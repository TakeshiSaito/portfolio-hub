from typing import cast
from uuid import UUID

import uvicorn
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from portfolio_hub import __description__, __title__, __version__, applications, installer
from portfolio_hub.applications import dto
from portfolio_hub.env import Env
from portfolio_hub.environment import TERMINAL, EnvironmentAlreadyExistsError
from portfolio_hub.launcher import FailedToResolveError
from portfolio_hub.project import ProjectAlreadyExistsError, ProjectNotFoundError


class Error(BaseModel):
    detail: str = Field(examples=["project foo does not exist"])


class NewName(BaseModel):
    name: str = Field(examples=["renamed"])


class NewEnvironment(BaseModel):
    name: str = Field(examples=["anim"])
    packages: list[dto.Package] = Field(examples=[[{"name": "greeter", "version": "2.0.0"}]])
    tools: list[str] = Field(default=[], examples=[["greet"]])
    default_tool: str = Field(default=str(TERMINAL), examples=["greet"])


class NewProject(BaseModel):
    name: str = Field(examples=["foo"])
    environments: list[NewEnvironment] = []


class Packages(BaseModel):
    packages: list[dto.Package] = Field(examples=[[{"name": "greeter_plugin", "version": "1.0.0"}]])


class Tools(BaseModel):
    tools: list[str] = Field(examples=[["greet"]])
    default_tool: str = Field(default=str(TERMINAL), examples=["greet"])


class NewLaunch(BaseModel):
    tool: str | None = Field(
        default=None,
        description="Name of the tool to launch, or terminal to open a terminal in the environment. Omit it to launch the default tool of the environment.",
        examples=["greet"],
    )


NOT_FOUND = {404: {"model": Error, "description": "The project or environment does not exist"}}
CONFLICT = {409: {"model": Error, "description": "The name is already used"}}
UNPROCESSABLE = {422: {"model": Error, "description": "The request breaks a rule, or the packages cannot be resolved"}}

router = APIRouter(prefix="/api")


def create_app() -> FastAPI:
    installer.get()
    app = FastAPI(title=__title__,
                  version=__version__,
                  description=__description__,
                  openapi_tags=[{"name": "projects", "description": "Projects, each holding its environments"},
                                {"name": "environments", "description": "The packages to resolve and the tools to launch"},
                                {"name": "packages", "description": "Packages that environments can use"},
                                {"name": "launches", "description": "Resolving an environment and launching a tool in it"},],
                  swagger_ui_parameters={"tryItOutEnabled": True})
    app.include_router(router)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    app.add_exception_handler(LookupError, _not_found)
    app.add_exception_handler(ProjectAlreadyExistsError, _conflict)
    app.add_exception_handler(EnvironmentAlreadyExistsError, _conflict)
    app.add_exception_handler(ValidationError, _invalid_value)
    app.add_exception_handler(RequestValidationError, _invalid_value)
    app.add_exception_handler(ValueError, _unprocessable)
    app.add_exception_handler(FailedToResolveError, _unprocessable)
    return app


def serve() -> None:
    env = Env()
    uvicorn.run(create_app(), host=env.host, port=env.port)


@router.get("/projects", tags=["projects"])
def list_projects() -> list[dto.Project]:
    return applications.list_projects()


@router.post("/projects", status_code=status.HTTP_201_CREATED, tags=["projects"], responses={**CONFLICT, **UNPROCESSABLE})
def create_project(body: NewProject) -> dto.Project:
    environments = [
        dto.NewEnvironment(name=environment.name, packages=environment.packages, tools=environment.tools, default_tool=environment.default_tool)
        for environment in body.environments
    ]
    return applications.create_project(body.name, environments)

@router.put("/projects/{project_id}/name", status_code=status.HTTP_204_NO_CONTENT, tags=["projects"], responses={**NOT_FOUND, **CONFLICT, **UNPROCESSABLE})
def rename_project(project_id: UUID, body: NewName) -> None:
    applications.rename_project(project_id, body.name)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["projects"], responses={**NOT_FOUND, **UNPROCESSABLE})
def delete_project(project_id: UUID) -> None:
    applications.delete_project(project_id)


@router.get("/projects/{project_id}/environments", tags=["environments"], responses={**NOT_FOUND, **UNPROCESSABLE})
def list_environments(project_id: UUID) -> list[dto.Environment]:
    if project_id not in [project.id for project in applications.list_projects()]:
        raise ProjectNotFoundError(f"project {project_id} does not exist")
    environments = applications.list_environments()
    return [environment for environment in environments if environment.project_id == project_id]


@router.post("/projects/{project_id}/environments", status_code=status.HTTP_201_CREATED, tags=["environments"], responses={**NOT_FOUND, **CONFLICT, **UNPROCESSABLE})
def create_environment(project_id: UUID, body: NewEnvironment) -> dto.Environment:
    packages = [(package.name, package.version) for package in body.packages]
    return applications.create_environment(project_id, body.name, packages, body.tools, body.default_tool)

@router.put("/environments/{environment_id}/name", status_code=status.HTTP_204_NO_CONTENT, tags=["environments"], responses={**NOT_FOUND, **CONFLICT, **UNPROCESSABLE})
def rename_environment(environment_id: UUID, body: NewName) -> None:
    applications.rename_environment(environment_id, body.name)


@router.put("/environments/{environment_id}/packages", status_code=status.HTTP_204_NO_CONTENT, tags=["environments"], responses={**NOT_FOUND, **UNPROCESSABLE})
def replace_packages(environment_id: UUID, body: Packages) -> None:
    packages = [(package.name, package.version) for package in body.packages]
    applications.replace_packages(environment_id, packages)


@router.put("/environments/{environment_id}/tools", status_code=status.HTTP_204_NO_CONTENT, tags=["environments"], responses={**NOT_FOUND, **UNPROCESSABLE})
def replace_tools(environment_id: UUID, body: Tools) -> None:
    applications.replace_tools(environment_id, body.tools, body.default_tool)


@router.delete("/environments/{environment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["environments"], responses={**NOT_FOUND, **UNPROCESSABLE})
def delete_environment(environment_id: UUID) -> None:
    applications.delete_environment(environment_id)


@router.get("/packages", tags=["packages"])
def list_packages() -> list[dto.Package]:
    return applications.list_packages()


@router.get("/environments/{environment_id}/resolved-packages", tags=["launches"], responses={**NOT_FOUND, **UNPROCESSABLE})
def resolve_environment(environment_id: UUID) -> list[dto.Package]:
    return applications.resolve_environment(environment_id)


@router.post("/environments/{environment_id}/launches", status_code=status.HTTP_201_CREATED, tags=["launches"], responses={**NOT_FOUND, **UNPROCESSABLE})
def launch(environment_id: UUID, body: NewLaunch) -> dto.Launch:
    return applications.launch(environment_id, body.tool)


def _not_found(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(error)})


def _conflict(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(error)})


def _invalid_value(request: Request, error: Exception) -> JSONResponse:
    message = "; ".join(detail["msg"] for detail in cast(ValidationError | RequestValidationError, error).errors())
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": message})


def _unprocessable(request: Request, error: Exception) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": str(error)})
