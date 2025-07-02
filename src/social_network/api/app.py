import fastapi
import fastapi.exceptions
import typing
import logging

from fastapi import encoders

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette import requests, responses, status

from src.social_network import settings, exceptions


class ApplicationRequestProtocol(typing.Protocol):
    settings: settings.SocialNetworkSettings
    logger: logging.Logger
    session_factory: async_sessionmaker[AsyncSession]


class Application(fastapi.FastAPI):
    app: ApplicationRequestProtocol

    def __init__(
        self, settings: settings.SocialNetworkSettings, logger: logging.Logger
    ):
        self.settings = settings
        self.logger = logger
        self.session_factory = async_sessionmaker(
            create_async_engine(
                url=settings.db.connection_url,
                echo=settings.level,
            ),
            expire_on_commit=False,
        )

        super().__init__(
            title="Social Network",
            description="OTUS Highload Architect (1.2.0)",
            debug=settings.level == "DEBUG",
        )

        self.include_router()
        self.add_exception_handler(
            fastapi.exceptions.RequestValidationError,
            self._validation_exception_handler,
        )
        self.add_exception_handler(
            exceptions.SocialNetworkError, self._social_network_exception_handler
        )

    def _validation_exception_handler(
        self, _: requests.Request, exc: Exception
    ) -> responses.Response:
        if not isinstance(exc, fastapi.exceptions.RequestValidationError):
            return responses.JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=encoders.jsonable_encoder(
                    {"message": repr(exc), "code": getattr(exc, "code", 0)}
                ),
            )
