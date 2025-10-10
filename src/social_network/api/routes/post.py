import typing
import uuid

import fastapi
from fastapi import status
from redis import asyncio as aioredis
from starlette import websockets

from social_network.api import dependencies, responses, schema_mappers
from social_network.api import models as dto

router = fastapi.APIRouter(prefix="/post")


@router.post(
    "/create",
    response_model=dto.PostDTO,
    response_description="Успешно создан пост",
    summary="Создание поста",
    description="Создание поста",
    operation_id="create_post",
    responses=responses.response_400
    | responses.response_401
    | responses.response_500
    | responses.response_503,
)
async def make_post(
    new_post: dto.NewPostDTO,
    request_user: dependencies.RequestUser,
    post_service: dependencies.PostService,
    feed_service: dependencies.FeedService,
) -> dto.PostDTO:
    post = await post_service.make_post(
        schema_mappers.PostMapper.map_new_dto_to_new_domain(
            new_post_dto=new_post, author_id=request_user.id
        )
    )
    await feed_service.add_post(user_id=request_user.id, post=post)
    return schema_mappers.PostMapper.map_domain_to_dto(post)


@router.put(
    "/update",
    response_model=dto.UpdatingPostDTO,
    response_description="Успешно изменен пост",
    summary="Изменение поста",
    description="Изменение поста",
    operation_id="update_post",
    responses={404: {"description": "Пост не найден"}}
    | responses.response_401
    | responses.response_500
    | responses.response_503,
)
async def update_post(
    updating_post: dto.UpdatingPostDTO,
    request_user: dependencies.RequestUser,
    post_service: dependencies.PostService,
    feed_service: dependencies.FeedService,
) -> dto.PostDTO:
    post = await post_service.update_post(
        post=schema_mappers.PostMapper.map_updating_dto_to_updating_domain(
            updating_post
        ),
        user_id=request_user.id,
    )
    await feed_service.update_post(user_id=request_user.id, post=post)
    return schema_mappers.PostMapper.map_domain_to_dto(post)


@router.put(
    "/delete/{id}",
    response_description="Успешно удален пост",
    summary="Удаление поста",
    description="Удаление поста",
    operation_id="delete_post",
    responses={404: {"description": "Пост не найден"}}
    | responses.response_401
    | responses.response_500
    | responses.response_503,
)
async def delete_post(
    id: typing.Annotated[uuid.UUID, fastapi.Path(title="Идентификатор поста")],
    request_user: dependencies.RequestUser,
    post_service: dependencies.PostService,
    feed_service: dependencies.FeedService,
) -> fastapi.Response:
    await post_service.delete_post(post_id=id, user_id=request_user.id)
    await feed_service.delete_post(user_id=request_user.id, post_id=id)
    return fastapi.Response(status_code=status.HTTP_200_OK)


@router.get(
    "/get/{id}",
    response_model=dto.PostDTO,
    response_description="Успешно получен пост",
    summary="Получение поста",
    description="Получение поста",
    operation_id="get_post",
    responses=responses.response_400
    | responses.response_401
    | {404: {"description": "Пост не найден"}}
    | responses.response_500
    | responses.response_503,
)
async def get_post(
    id: typing.Annotated[str, fastapi.Path(title="Идентификатор поста")],
    post_service: dependencies.PostService,
) -> dto.PostDTO:
    post = await post_service.get_post(post_id=uuid.UUID(id))
    return schema_mappers.PostMapper.map_domain_to_dto(post)


@router.get(
    "/feed",
    response_model=list[dto.PostDTO],
    response_description="Успешно получены посты друзей",
    summary="Поиск постов друзей",
    description="Поиск постов друзей",
    operation_id="feed_posts",
    responses=responses.response_400 | responses.response_500 | responses.response_503,
)
async def feed_posts(
    request_user: dependencies.RequestUser,
    feed_service: dependencies.FeedService,
    post_service: dependencies.PostService,
    offset: typing.Annotated[int, fastapi.Query(examples=[100])] = 100,
    limit: typing.Annotated[int, fastapi.Query(examples=[10])] = 10,
) -> list[dto.PostDTO]:
    try:
        posts = await feed_service.feed(
            user_id=request_user.id, offset=offset, limit=limit
        )
    except aioredis.RedisError:
        posts = await post_service.feed(
            user_id=request_user.id, offset=offset, limit=limit
        )
    return [schema_mappers.PostMapper.map_domain_to_dto(post) for post in posts]


@router.websocket("/post/feed/posted")
async def ws_post_feed(
    websocket: websockets.WebSocket,
    ws_manager: dependencies.WsManager,
    request_user: dependencies.RequestUser,
) -> None:
    """
    Устанавливает вэб-сокет соединение для отправки постов в режиме реального времени
    """
    await ws_manager.connect(websocket, request_user)
    while True:
        try:
            await websocket.receive_text()
        except websockets.WebSocketDisconnect:
            ws_manager.disconnect(websocket)
            break
