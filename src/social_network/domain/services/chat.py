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
    def _make_dialog_key(user_id: uuid.UUID, friend_id: uuid.UUID) -> str:
        return f"dialog:{str(user_id)}:{str(friend_id)}"

    @staticmethod
    def _make_messages_key(dialog_id: uuid.UUID) -> str:
        return f"messages:{str(dialog_id)}"

    async def is_valid(self) -> bool:
        try:
            functions = await self._redis.function_list()
            print(f"🔍 Отладка: function_list() вернул: {functions}")

            if not functions:
                return False

            # Проверяем наличие нужных функций
            required_functions = [
                "make_dialog",
                "get_dialog",
                "write_message",
                "show_messages",
            ]

            loaded_functions = []

            # Обрабатываем результат function_list
            # Формат: [['library_name', 'chat_functions', 'engine', 'LUA', 'functions', [функции...]]]
            if isinstance(functions, list) and len(functions):
                for lib_data in functions:
                    print(f"🔍 Отладка: обрабатываем библиотеку: {lib_data}")
                    if isinstance(lib_data, list) and len(lib_data) >= 6:
                        # Ищем индекс 'functions' в списке
                        try:
                            functions_index = lib_data.index("functions")
                            if functions_index + 1 < len(lib_data):
                                functions_list = lib_data[functions_index + 1]
                                print(f"🔍 Отладка: список функций: {functions_list}")

                                if isinstance(functions_list, list):
                                    for func_data in functions_list:
                                        if (
                                            isinstance(func_data, list)
                                            and len(func_data) >= 2
                                        ):
                                            # Ищем индекс 'name' в списке функции
                                            try:
                                                name_index = func_data.index("name")
                                                if name_index + 1 < len(func_data):
                                                    func_name = func_data[
                                                        name_index + 1
                                                    ]
                                                    loaded_functions.append(func_name)
                                                    print(
                                                        f"🔍 Найдена функция: {func_name}"
                                                    )
                                            except ValueError:
                                                continue
                        except ValueError:
                            continue

            print(f"🔍 Отладка: найденные функции: {loaded_functions}")

            missing_functions = [
                f for f in required_functions if f not in loaded_functions
            ]
            if missing_functions:
                print(f"Отсутствуют UDF функции: {missing_functions}")
                return False

            print(f"✅ UDF функции проверены: {loaded_functions}")
            return True

        except Exception as e:
            print(f"❌ Ошибка проверки UDF функций: {e}")
            import traceback

            print(f"🔍 Трассировка: {traceback.format_exc()}")
            return False

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
        await self._redis.fcall(
            function="make_dialog",
            numkeys=1,
            keys_and_args=(
                self._make_dialog_key(user_id=user.id, friend_id=friend_id),
                chat.model_dump_json(),
            ),
        )
        return chat

    async def write_message(
        self, user_id: uuid.UUID, friend_id: uuid.UUID, message: str
    ) -> None:
        for chat_id in (
            self._make_dialog_key(user_id=user_id, friend_id=friend_id),
            self._make_dialog_key(user_id=friend_id, friend_id=user_id),
        ):
            dialog = await self._redis.fcall(
                function="get_dialog",
                numkeys=1,
                keys_and_args=(chat_id,),
            )
            if not dialog:
                continue

            dialog_id = models.ChatDomain(**json.loads(dialog)).id
            await self._redis.fcall(
                function="write_message",
                numkeys=1,
                keys_and_args=(
                    self._make_messages_key(dialog_id),
                    models.ChatMessageDomain(
                        id=uuid.uuid4(),
                        author_id=user_id,
                        chat_id=dialog_id,
                        text=message,
                    ).model_dump_json(),
                    datetime.datetime.now(datetime.timezone.utc).timestamp(),
                ),
            )
            return None

        raise domain_exceptions.DialogNotFoundError(
            user_id=str(user_id), friend_id=str(friend_id)
        )

    async def show_messages(
        self, user: models.UserDomain, friend_id: uuid.UUID
    ) -> list[models.ChatMessageDomain]:
        for chat_id in (
            self._make_dialog_key(user_id=user.id, friend_id=friend_id),
            self._make_dialog_key(user_id=friend_id, friend_id=user.id),
        ):
            dialog = await self._redis.fcall(
                function="get_dialog",
                numkeys=1,
                keys_and_args=(chat_id,),
            )
            if not dialog:
                continue

            dialog_id = models.ChatDomain(**json.loads(dialog)).id
            messages = await self._redis.fcall(
                function="show_messages",
                numkeys=1,
                keys_and_args=(self._make_messages_key(dialog_id),),
            )
            return [
                models.ChatMessageDomain(**json.loads(message)) for message in messages
            ]

        return []
