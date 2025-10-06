import typing

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from social_network.infrastructure.database import repository
from social_network.infrastructure.database.uow import abstract


class ChatUnitOfWork(abstract.AbstractUnitOfWork):
    def __init__(
        self,
        database_name: str,
        chat_repository: repository.ChatRepository,
        chat_participant_repository: repository.ChatParticipantRepository,
        chat_message_repository: repository.ChatMessageRepository,
        user_repository: repository.UserRepository,
        master_factory: async_sessionmaker[AsyncSession],
        slave_factory: typing.Optional[async_sessionmaker[AsyncSession]] = None,
        timeout_seconds: int = 0,
    ) -> None:
        super().__init__(
            database_name=database_name,
            master_factory=master_factory,
            slave_factory=slave_factory,
            timeout_seconds=timeout_seconds,
        )

        self.chats = chat_repository
        self.participants = chat_participant_repository
        self.messages = chat_message_repository
        self.users = user_repository

    async def _init_repositories(
        self, session: typing.Optional[AsyncSession] = None
    ) -> None:
        self.chats(session)
        self.participants(session)
        self.messages(session)
        self.users(session)
