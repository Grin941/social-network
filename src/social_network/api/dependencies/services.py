import typing

import fastapi
from starlette import requests

from social_network.domain import services
from social_network.infrastructure.database import repository, uow


async def get_auth_service(request: requests.Request) -> services.AuthService:
    return services.AuthService(
        unit_of_work=uow.UserUnitOfWork(
            database_name=request.state.settings.db.name,
            master_factory=request.state.master_factory,
            slave_factory=request.state.slave_factory,
            user_repository=repository.UserRepository(),
        ),
        secret=request.state.settings.auth.secret,
        algorithm=request.state.settings.auth.algorithm,
        token_ttl_seconds=request.state.settings.auth.token_ttl_seconds,
    )


async def get_user_service(request: requests.Request) -> services.UserService:
    return services.UserService(
        unit_of_work=uow.UserUnitOfWork(
            database_name=request.state.settings.db.name,
            master_factory=request.state.master_factory,
            slave_factory=request.state.slave_factory,
            user_repository=repository.UserRepository(),
        ),
    )


async def get_friend_service(request: requests.Request) -> services.FriendService:
    return services.FriendService(
        unit_of_work=uow.FriendUnitOfWork(
            database_name=request.state.settings.db.name,
            master_factory=request.state.master_factory,
            slave_factory=request.state.slave_factory,
            friend_repository=repository.FriendRepository(),
        ),
    )


async def get_post_service(request: requests.Request) -> services.PostService:
    return services.PostService(
        unit_of_work=uow.PostUnitOfWork(
            database_name=request.state.settings.db.name,
            master_factory=request.state.master_factory,
            slave_factory=request.state.slave_factory,
            post_repository=repository.PostRepository(),
        ),
    )


async def get_feed_service(request: requests.Request) -> services.FeedService:
    return services.FeedService(
        unit_of_work=uow.FeedUnitOfWork(
            database_name=request.state.settings.db.name,
            master_factory=request.state.master_factory,
            slave_factory=request.state.slave_factory,
            post_repository=repository.PostRepository(),
            friend_repository=repository.FriendRepository(),
        ),
        redis=request.state.redis,
        cache_capacity=request.state.settings.redis.feed_capacity,
        ttl=request.state.settings.redis.ttl,
        lock_timeout=request.state.settings.redis.lock_timeout,
    )


AuthService = typing.Annotated[services.AuthService, fastapi.Depends(get_auth_service)]
UserService = typing.Annotated[services.UserService, fastapi.Depends(get_user_service)]
FriendService = typing.Annotated[
    services.FriendService, fastapi.Depends(get_friend_service)
]
PostService = typing.Annotated[services.PostService, fastapi.Depends(get_post_service)]
FeedService = typing.Annotated[services.FeedService, fastapi.Depends(get_feed_service)]
