import typing

import fastapi
from starlette import requests
from starlette.datastructures import State

from social_network.domain import services
from social_network.infrastructure.database import repository, uow


def _get_auth_service(state: State) -> services.AuthService:
    return services.AuthService(
        unit_of_work=uow.UserUnitOfWork(
            database_name=state.settings.db.name,
            master_factory=state.master_factory,
            slave_factory=state.slave_factory,
            user_repository=repository.UserRepository(),
        ),
        secret=state.settings.auth.secret,
        algorithm=state.settings.auth.algorithm,
        token_ttl_seconds=state.settings.auth.token_ttl_seconds,
    )


async def get_auth_service(request: requests.Request) -> services.AuthService:
    return _get_auth_service(request.state)


async def get_ws_auth_service(websocket: fastapi.WebSocket) -> services.AuthService:
    return _get_auth_service(websocket.state)


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


async def get_async_ws_feed_service(
    websocket: fastapi.WebSocket,
) -> services.AsyncFeedService:
    return await services.AsyncFeedService.create(websocket.state.rmq)


async def get_async_feed_service(
    request: requests.Request,
) -> services.AsyncFeedService:
    return await services.AsyncFeedService.create(request.state.rmq)


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
        async_feed_service=await get_async_feed_service(request),
        cache_capacity=request.state.settings.redis.feed_capacity,
        ttl=request.state.settings.redis.ttl,
        lock_timeout=request.state.settings.redis.lock_timeout,
        celebrity_friends_threshold=request.state.settings.celebrity_friends_threshold,
    )


async def get_chat_service(request: requests.Request) -> services.AbstractChatService:
    unit_of_work = uow.ChatUnitOfWork(
        database_name=request.state.settings.db.name,
        master_factory=request.state.master_factory,
        slave_factory=request.state.slave_factory,
        chat_repository=repository.ChatRepository(),
        chat_participant_repository=repository.ChatParticipantRepository(),
        chat_message_repository=repository.ChatMessageRepository(),
        user_repository=repository.UserRepository(),
    )
    if request.state.settings.redis_udf_is_enabled:
        udf_service = services.RedisUDFChatService(
            unit_of_work=unit_of_work,
            redis_client=request.state.redis,
        )
        if udf_service.is_valid():
            return udf_service
    return services.ChatService(unit_of_work=unit_of_work)


AuthService = typing.Annotated[services.AuthService, fastapi.Depends(get_auth_service)]
WsAuthService = typing.Annotated[
    services.AuthService, fastapi.Depends(get_ws_auth_service)
]
UserService = typing.Annotated[services.UserService, fastapi.Depends(get_user_service)]
FriendService = typing.Annotated[
    services.FriendService, fastapi.Depends(get_friend_service)
]
PostService = typing.Annotated[services.PostService, fastapi.Depends(get_post_service)]
AsyncWsFeedService = typing.Annotated[
    services.AsyncFeedService, fastapi.Depends(get_async_ws_feed_service)
]
FeedService = typing.Annotated[services.FeedService, fastapi.Depends(get_feed_service)]
ChatService = typing.Annotated[
    services.AbstractChatService, fastapi.Depends(get_chat_service)
]
