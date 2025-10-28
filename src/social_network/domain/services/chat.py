import abc
import asyncio
import datetime
import json
import typing
import uuid

from redis import asyncio as aioredis

from social_network.domain import exceptions as domain_exceptions
from social_network.domain import models
from social_network.domain.models import UserDomain
from social_network.domain.services import abstract
from social_network.infrastructure.database import (
    exceptions as database_exceptions,
)
from social_network.infrastructure.database import (
    uow,
)


class AbstractChatService(abstract.AbstractService):
    @abc.abstractmethod
    async def make_dialog(
        self, user: models.UserDomain, friend_id: uuid.UUID
    ) -> models.ChatDomain: ...

    @abc.abstractmethod
    async def write_message(
        self, user: models.UserDomain, friend_id: uuid.UUID, text: str
    ) -> models.ChatMessageDomain: ...

    @abc.abstractmethod
    async def show_messages(
        self, user: models.UserDomain, friend_id: uuid.UUID
    ) -> list[models.ChatMessageDomain]: ...

    @staticmethod
    def _make_chat_name(user: UserDomain, friend: UserDomain) -> str:
        return f"{user.second_name} – {friend.second_name} chat"


class ChatService(AbstractChatService):
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


class RedisUDFChatService(AbstractChatService):
    def __init__(
        self, unit_of_work: uow.AbstractUnitOfWork, redis_client: aioredis.Redis
    ) -> None:
        super().__init__(unit_of_work)
        self._redis = redis_client

    @property
    def uow(self) -> uow.ChatUnitOfWork:
        return typing.cast(uow.ChatUnitOfWork, self._uow)

    @staticmethod
    def make_dialog_key(user_id: uuid.UUID, friend_id: uuid.UUID) -> str:
        return f"dialog:{str(user_id)}:{str(friend_id)}"

    @staticmethod
    def make_messages_key(dialog_id: uuid.UUID) -> str:
        return f"messages:{str(dialog_id)}"

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

        chat = models.ChatDomain(
            id=uuid.uuid4(),
            name=self._make_chat_name(user=user, friend=friend),
        )
        await self._redis.fcall(  # type: ignore[misc]
            "make_dialog",
            1,
            self.make_dialog_key(user_id=user.id, friend_id=friend_id),
            chat.model_dump_json(),
        )
        return chat

    async def write_message(
        self, user: models.UserDomain, friend_id: uuid.UUID, text: str
    ) -> models.ChatMessageDomain:
        for chat_id in (
            self.make_dialog_key(user_id=user.id, friend_id=friend_id),
            self.make_dialog_key(user_id=friend_id, friend_id=user.id),
        ):
            dialog = await self._redis.fcall(  # type: ignore[misc]
                "get_dialog",
                1,
                chat_id,
            )
            if not dialog:
                continue

            dialog_id = models.ChatDomain(**json.loads(dialog)).id
            message = models.ChatMessageDomain(
                id=uuid.uuid4(),
                author_id=user.id,
                chat_id=dialog_id,
                text=text,
            )
            await self._redis.fcall(  # type: ignore[misc]
                "write_message",
                1,
                self.make_messages_key(dialog_id),
                message.model_dump_json(),
                datetime.datetime.now(datetime.timezone.utc).timestamp(),
            )
            return message

        raise domain_exceptions.DialogNotFoundError(
            user_id=str(user.id), friend_id=str(friend_id)
        )

    async def show_messages(
        self, user: models.UserDomain, friend_id: uuid.UUID
    ) -> list[models.ChatMessageDomain]:
        for chat_id in (
            self.make_dialog_key(user_id=user.id, friend_id=friend_id),
            self.make_dialog_key(user_id=friend_id, friend_id=user.id),
        ):
            dialog = await self._redis.fcall(  # type: ignore[misc]
                "get_dialog",
                1,
                chat_id,
            )
            if not dialog:
                continue

            dialog_id = models.ChatDomain(**json.loads(dialog)).id
            messages = await self._redis.fcall(  # type: ignore[misc]
                "show_messages",
                1,
                self.make_messages_key(dialog_id),
            )
            return [
                models.ChatMessageDomain(**json.loads(message)) for message in messages
            ]

        return []
