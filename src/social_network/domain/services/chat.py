import asyncio
import typing
import uuid

from social_network.domain import exceptions as domain_exceptions
from social_network.domain import models
from social_network.domain.services import abstract
from social_network.infrastructure.database import (
    exceptions as database_exceptions,
)
from social_network.infrastructure.database import (
    uow,
)


class ChatService(abstract.AbstractService):
    @property
    def uow(self) -> uow.ChatUnitOfWork:
        return typing.cast(uow.ChatUnitOfWork, self._uow)

    async def make_dialog(
        self, user: models.UserDomain, friend_id: uuid.UUID
    ) -> models.ChatDomain:
        async for _ in self.uow.transaction():
            try:
                friend = await self.uow.users.find_one(str(friend_id))
            except database_exceptions.ObjectDoesNotExistError as err:
                raise domain_exceptions.FriendNotFoundError(
                    user_id=str(user.id), friend_id=str(friend_id)
                ) from err
            dialog = await self.uow.chats.create(
                models.NewChatDomain(
                    name=f"{user.second_name} – {friend.second_name} chat"
                )
            )
            await asyncio.gather(
                self.uow.participants.create(
                    models.NewChatParticipantDomain(
                        user_id=user.id,
                        chat_id=dialog.id,
                    )
                ),
                self.uow.participants.create(
                    models.NewChatParticipantDomain(
                        user_id=friend.id,
                        chat_id=dialog.id,
                    )
                ),
            )
        return dialog

    async def write_message(
        self, user: models.UserDomain, friend_id: uuid.UUID, text: str
    ) -> models.ChatMessageDomain:
        async for _ in self.uow.transaction():
            dialog_id = await self.uow.chats.find_dialog_id(
                user_id=str(user.id), friend_id=str(friend_id)
            )
            if dialog_id is None:
                raise domain_exceptions.DialogNotFoundError(
                    user_id=str(user.id), friend_id=str(friend_id)
                )

            message = await self.uow.messages.create(
                models.NewChatMessageDomain(
                    author_id=user.id,
                    chat_id=dialog_id,
                    text=text,
                )
            )
        return message

    async def show_messages(
        self, user: models.UserDomain, friend_id: uuid.UUID
    ) -> list[models.ChatMessageDomain]:
        async for _ in self.uow.transaction():
            dialog_id = await self.uow.chats.find_dialog_id(
                user_id=str(user.id), friend_id=str(friend_id)
            )
            if dialog_id is None:
                raise domain_exceptions.DialogNotFoundError(
                    user_id=str(user.id), friend_id=str(friend_id)
                )

            messages = await self.uow.messages.find_all(
                filters={"chat_id": dialog_id},
                order_by="created_at desc",
            )
        return messages
