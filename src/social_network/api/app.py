import logging

import fastapi
import typing
import datetime
import contextlib

import sentry_sdk
from fastapi import encoders, exceptions as fastapi_exceptions

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette import requests, responses, status

from social_network import settings
from social_network.api.routes import user as user_routes, login as login_routes
from social_network.api.models import common
from social_network.api import requests as api_requests
from social_network.database import exceptions as db_exceptions
from social_network.domain import exceptions as domain_exceptions


logger = logging.getLogger(__name__)


async def _validation_exception_handler(
    request: requests.Request, exc: Exception
) -> responses.JSONResponse:
    to_capture_exception = False
    if isinstance(exc, fastapi_exceptions.RequestValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, db_exceptions.ObjectDoesNotExistError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, domain_exceptions.AuthError):
        status_code = status.HTTP_401_UNAUTHORIZED
        to_capture_exception = True
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        to_capture_exception = True

    if to_capture_exception:
        logger.exception(exc)
        sentry_sdk.capture_exception(exc)

    error_code = getattr(exc, "code", None)
    if not isinstance(error_code, int):
        error_code = 0

    return responses.JSONResponse(
        status_code=status_code,
        content=encoders.jsonable_encoder(
            common.ErrorMessage(
                message=str(exc),
                code=error_code,
                request_id=api_requests.get_request_id(),
            )
        ),
        headers={"Retry-After": str(60 - datetime.datetime.now().second)},
    )


class ApplicationState(typing.TypedDict):
    settings: settings.SocialNetworkSettings
    session_factory: async_sessionmaker[AsyncSession]


@contextlib.asynccontextmanager
async def lifespan(
    app: fastapi.FastAPI,
) -> typing.AsyncGenerator[ApplicationState, None]:
    social_network_settings = settings.SocialNetworkSettings()
    app.debug = social_network_settings.level == "DEBUG"

    engine = create_async_engine(
        url=social_network_settings.db.connection_url,
        echo=social_network_settings.level == "DEBUG",
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    yield ApplicationState(
        settings=social_network_settings,
        session_factory=session_factory,
    )

    await engine.dispose()


def customize_openapi(app: fastapi.FastAPI) -> None:
    for _, method_item in app.openapi().get("paths", {}).items():
        for _, param in method_item.items():
            api_responses = param.get("responses")
            # remove 422 response, also can remove other status code
            if "422" in api_responses:
                del api_responses["422"]


def build_application() -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        title="Social Network",
        description="OTUS Highload Architect (1.2.0)",
        exception_handlers={
            Exception: _validation_exception_handler,
        },
        lifespan=lifespan,
    )
    app.include_router(login_routes.router)
    app.include_router(user_routes.router)
    app.add_middleware(api_requests.RequestIdMiddleware)

    customize_openapi(app)

    return app
