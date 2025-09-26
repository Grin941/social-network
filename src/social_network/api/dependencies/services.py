import typing

import fastapi
from starlette import requests

from social_network.domain.services import auth, user
from social_network.infrastructure.database import repository, uow


async def get_auth_service(request: requests.Request) -> auth.AuthService:
    return auth.AuthService(
        unit_of_work=uow.UnitOfWork(
            master_factory=request.state.master_factory,
            slave_factory=request.state.slave_factory,
            user_repository=repository.UserRepository(),
        ),
        secret=request.state.settings.auth.secret,
        algorithm=request.state.settings.auth.algorithm,
        token_ttl_seconds=request.state.settings.auth.token_ttl_seconds,
    )


async def get_user_service(request: requests.Request) -> user.UserService:
    return user.UserService(
        unit_of_work=uow.UnitOfWork(
            master_factory=request.state.master_factory,
            slave_factory=request.state.slave_factory,
            user_repository=repository.UserRepository(),
        ),
    )


AuthService = typing.Annotated[auth.AuthService, fastapi.Depends(get_auth_service)]
UserService = typing.Annotated[user.UserService, fastapi.Depends(get_user_service)]
