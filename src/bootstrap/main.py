import asyncio
import logging
import random
import threading
import typing
import uuid

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bootstrap import settings, uow
from data_generator import const, generator
from social_network.domain import models
from social_network.domain.services import auth
from social_network.infrastructure.database import repository

# Global variables for the async event loop and thread
_async_loop = None
_async_thread = None
_loop_lock = threading.Lock()

logger = logging.getLogger(__name__)


class Bootstrap:
    def __init__(self) -> None:
        self._settings = settings.BootstrapSettings()
        self._settings.print_to_log()

        self._uow = uow.BootstrapUnitOfWork(
            database_name=self._settings.db.name,
            user_repository=uow.UserRepository(),
            friend_repository=repository.FriendRepository(),
            post_repository=repository.PostRepository(),
            chat_repository=repository.ChatRepository(),
            chat_participant_repository=repository.ChatParticipantRepository(),
            chat_message_repository=repository.ChatMessageRepository(),
            master_factory=async_sessionmaker(
                create_async_engine(
                    url=self._settings.db.connection_url,
                    echo=self._settings.log_level == "DEBUG",
                    pool_size=self._settings.db.pool_size,
                ),
                expire_on_commit=False,
            ),
        )
        self._generator = generator.DataGenerator(
            seed=self._settings.generator.seed,
            locale=self._settings.generator.locale,
        )

    @staticmethod
    def _start_async_loop() -> None:
        """Starts the asyncio event loop in a new thread."""
        global _async_loop
        global _async_thread
        with _loop_lock:
            if _async_loop is None:
                _async_loop = asyncio.new_event_loop()
                _async_thread = threading.Thread(
                    target=_async_loop.run_forever, daemon=True
                )
                _async_thread.start()

    def _run_async(self, coro) -> typing.Any:
        """Runs an async coroutine from a synchronous function."""
        self._start_async_loop()
        future = asyncio.run_coroutine_threadsafe(
            coro, typing.cast(asyncio.AbstractEventLoop, _async_loop)
        )
        return future.result()

    @staticmethod
    def _make_friends(
        user_id: uuid.UUID, friend_id: uuid.UUID
    ) -> list[models.NewFriendDomain]:
        return [
            models.NewFriendDomain(
                user_id=user_id,
                friend_id=friend_id,
            ),
            models.NewFriendDomain(
                user_id=friend_id,
                friend_id=user_id,
            ),
        ]

    def _make_user(self, user: models.NewUserDomain) -> models.NewUserDomain:
        return models.NewUserDomain(
            **user.model_dump(exclude={"password"}),
            password=auth.encrypt_password(
                password=user.password, secret=self._settings.auth.secret
            ),
        )

    async def _make_user_entities(
        self,
        user_id: uuid.UUID,
    ) -> int:
        await self._uow.posts.batch_create(
            list(
                self._generator.generate_posts(
                    user_id=user_id,
                    entities_count=random.randint(
                        min(20, self._settings.generator.max_posts_per_user_count),
                        self._settings.generator.max_posts_per_user_count,
                    ),
                )
            )
        )
        friends_count = random.randint(
            min(50, self._settings.generator.max_user_friends_count),
            self._settings.generator.max_user_friends_count,
        )
        users = await self._uow.users.batch_create(
            [
                self._make_user(_)
                for _ in self._generator.generate_users(
                    entities_count=friends_count, password=self._settings.my_password
                )
            ]
        )

        friends_to_make = []
        posts_to_make = []
        chat_participants_to_make = []
        messages_to_make = []
        for user in users:
            friends_to_make.extend(
                self._make_friends(user_id=user_id, friend_id=user.id)
            )
            posts_to_make.extend(
                list(
                    self._generator.generate_posts(
                        user_id=user.id,
                        entities_count=random.randint(
                            1, self._settings.generator.max_posts_per_user_count
                        ),
                    )
                )
            )
            chat = await self._uow.chats.create(
                self._generator.generate_dialog(user_id=user_id, friend_id=user.id)
            )
            chat_participants_to_make.extend(
                [
                    self._generator.generate_dialog_participant(
                        user_id=user_id, chat_id=chat.id
                    ),
                    self._generator.generate_dialog_participant(
                        user_id=user.id, chat_id=chat.id
                    ),
                ]
            )
            messages_to_make.extend(
                [
                    self._generator.generate_message(user_id=user_id, chat_id=chat.id),
                    self._generator.generate_message(user_id=user.id, chat_id=chat.id),
                ]
            )

        await asyncio.gather(
            self._uow.friends.batch_create(friends_to_make),
            self._uow.posts.batch_create(posts_to_make),
            self._uow.participants.batch_create(chat_participants_to_make),
            self._uow.messages.batch_create(messages_to_make),
        )

        return friends_count

    async def _bootstrap(self) -> None:
        logger.info("Bootstrap started")
        async for transaction in self._uow.transaction():
            count = (
                await transaction.execute_raw_query("SELECT COUNT(*) FROM users")
            ).scalar()
        if not count:
            async for _ in self._uow.transaction():
                myself = await self._uow.users.create_myself(
                    item=self._make_user(
                        self._generator.generate_user(
                            sex=const.MALE,
                            password=self._settings.my_password,
                        )
                    ),
                    id_=self._settings.my_uuid,
                )
                friends_count = await self._make_user_entities(myself.id)
            logger.info(f"Generated {friends_count} my friends")
            users_to_create_cnt = self._settings.generator.users_count - (
                friends_count + 1
            )
        else:
            users_to_create_cnt = self._settings.generator.users_count - count
        while users_to_create_cnt > 0:
            async for _ in self._uow.transaction():
                user = await self._uow.users.create(
                    self._generator.generate_user(password=self._settings.my_password)
                )
                friends_count = await self._make_user_entities(user.id)
            logger.info(f"Generated {friends_count} '{user.id}' friends")
            users_to_create_cnt -= friends_count + 1
        logger.info("Bootstrap finished")

    def bootstrap(self) -> None:
        self._run_async(self._bootstrap())


if __name__ == "__main__":
    Bootstrap().bootstrap()
