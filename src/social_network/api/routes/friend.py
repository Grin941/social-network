import asyncio
import typing
import uuid

import fastapi
from fastapi import status

from social_network.api import dependencies, responses, schema_mappers
from social_network.api import models as dto

router = fastapi.APIRouter(prefix="/friend")


@router.put(
    "/set/{user_id}",
    response_model=dto.FriendDTO,
    response_description="Пользователь успешно указал своего друга",
    summary="Добавление пользователя в друзья",
    description="Добавление пользователя в друзья",
    operation_id="set_friend",
    responses={404: {"description": "Пользователь не найден"}}
    | responses.response_401
    | responses.response_500
    | responses.response_503,
)
async def set_friend(
    user_id: typing.Annotated[uuid.UUID, fastapi.Path(title="Идентификатор друга")],
    request_user: dependencies.RequestUser,
    friend_service: dependencies.FriendService,
    feed_service: dependencies.FeedService,
    chat_service: dependencies.ChatService,
) -> dto.FriendDTO:
    friendship, _ = await asyncio.gather(
        friend_service.make_friendship(user=request_user, friend_id=user_id),
        chat_service.make_dialog(user=request_user, friend_id=user_id),
    )
    await feed_service.add_friend(user_id=request_user.id, friend_id=user_id)
    return schema_mappers.FriendMapper.map_domain_to_dto(friendship)


@router.put(
    "/delete/{user_id}",
    response_description="Пользователь успешно удалил из друзей пользователя",
    summary="Удаление пользователя из друзей",
    description="Удаление пользователя из друзей",
    operation_id="delete_friend",
    responses={404: {"description": "Пользователь не найден"}}
    | responses.response_401
    | responses.response_500
    | responses.response_503,
)
async def delete_friend(
    user_id: typing.Annotated[uuid.UUID, fastapi.Path(title="Идентификатор друга")],
    request_user: dependencies.RequestUser,
    friend_service: dependencies.FriendService,
    feed_service: dependencies.FeedService,
) -> fastapi.Response:
    await friend_service.delete_friendship(user=request_user, friend_id=user_id)
    await feed_service.delete_friend(user_id=request_user.id, friend_id=user_id)
    return fastapi.Response(status_code=status.HTTP_200_OK)
