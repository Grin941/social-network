from src.social_network.domain.services import auth, user
from src.social_network.api import app
from starlette import requests
import typing
import fastapi
from src.social_network.database import uow, repository


async def get_auth_service(request: requests.Request) -> auth.AuthService:
    app_state = typing.cast(app.ApplicationState, request.state)

    return auth.AuthService(
        unit_of_work=uow.UnitOfWork(
            session_factory=app_state.session_factory,
            user_repository=repository.UserRepository(),
            logger=app_state.logger,
        ),
        logger=app_state.logger,
        secret=app_state.settings.auth.secret,
        algorithm=app_state.settings.auth.algorithm,
    )


async def get_user_service(request: requests.Request) -> user.UserService:
    app_state = typing.cast(app.ApplicationState, request.state)

    return user.UserService(
        unit_of_work=uow.UnitOfWork(
            session_factory=app_state.session_factory,
            user_repository=repository.UserRepository(),
            logger=app_state.logger,
        ),
        logger=app_state.logger,
    )


AuthService = typing.Annotated[auth.AuthService, fastapi.Depends(get_auth_service)]
UserService = typing.Annotated[user.UserService, fastapi.Depends(get_user_service)]
