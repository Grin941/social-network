from social_network.domain.services import auth, user
from starlette import requests
import typing
import fastapi
from social_network.database import uow, repository


async def get_auth_service(request: requests.Request) -> auth.AuthService:
    return auth.AuthService(
        unit_of_work=uow.UnitOfWork(
            session_factory=request.state.session_factory,
            user_repository=repository.UserRepository(),
            logger=request.state.logger,
        ),
        logger=request.state.logger,
        secret=request.state.settings.auth.secret,
        algorithm=request.state.settings.auth.algorithm,
    )


async def get_user_service(request: requests.Request) -> user.UserService:
    return user.UserService(
        unit_of_work=uow.UnitOfWork(
            session_factory=request.state.session_factory,
            user_repository=repository.UserRepository(),
            logger=request.state.logger,
        ),
        logger=request.state.logger,
    )


AuthService = typing.Annotated[auth.AuthService, fastapi.Depends(get_auth_service)]
UserService = typing.Annotated[user.UserService, fastapi.Depends(get_user_service)]
