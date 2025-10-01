import typing
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from social_network.domain import models
from social_network.infrastructure.database import repository
from social_network.infrastructure.database.uow import abstract


class UserRepository(repository.UserRepository):
    async def create_myself(
        self, item: models.NewUserDomain, id_: uuid.UUID
    ) -> models.UserDomain:
        session = self._get_db_session()
        await session.execute(
            self._create_statement,
            item.model_dump() | {"id": str(id_)},
        )

        return await self.find_one(str(id_))


class BootstrapUnitOfWork(abstract.AbstractUnitOfWork):
    def __init__(
        self,
        database_name: str,
        user_repository: UserRepository,
        friend_repository: repository.FriendRepository,
        post_repository: repository.PostRepository,
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

        self.users = user_repository
        self.friends = friend_repository
        self.posts = post_repository

    async def _init_repositories(
        self, session: typing.Optional[AsyncSession] = None
    ) -> None:
        self.users(session)
        self.friends(session)
        self.posts(session)
