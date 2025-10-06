import typing
import uuid

import fastapi
from fastapi import status

from social_network.api import dependencies, responses, schema_mappers
from social_network.api import models as dto

router = fastapi.APIRouter(prefix="/dialog")


@router.post(
    "/{user_id}/send",
    response_description="Успешно отправлено сообщение",
    summary="Отправка сообщения в диалог",
    description="Отправка сообщения в диалог",
    operation_id="send_dialog_message",
    responses={404: {"description": "Диалог не найден"}}
    | responses.response_401
    | responses.response_500
    | responses.response_503,
)
async def send_dialog_message(
    user_id: typing.Annotated[uuid.UUID, fastapi.Path(title="Идентификатор друга")],
    message: dto.NewMessageDTO,
    request_user: dependencies.RequestUser,
    chat_service: dependencies.ChatService,
) -> fastapi.Response:
    await chat_service.write_message(
        user=request_user,
        friend_id=user_id,
        text=message.text,
    )
    return fastapi.Response(status_code=status.HTTP_200_OK)


@router.get(
    "/{user_id}/list",
    response_model=list[dto.MessageDTO],
    response_description="Диалог между двумя пользователями",
    summary="Диалог между двумя пользователями",
    description="Диалог между двумя пользователями",
    operation_id="list_dialog",
    responses={404: {"description": "Диалог не найден"}}
    | responses.response_401
    | responses.response_500
    | responses.response_503,
)
async def list_dialog(
    user_id: typing.Annotated[uuid.UUID, fastapi.Path(title="Идентификатор друга")],
    request_user: dependencies.RequestUser,
    chat_service: dependencies.ChatService,
) -> list[dto.MessageDTO]:
    messages = await chat_service.show_messages(user=request_user, friend_id=user_id)
    return [
        schema_mappers.MessageMapper.map_domain_to_dto(
            message=message, user_id=request_user.id, friend_id=user_id
        )
        for message in messages
    ]
