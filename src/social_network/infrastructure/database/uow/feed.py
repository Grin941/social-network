import typing

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from social_network.infrastructure.database import repository
from social_network.infrastructure.database.uow import abstract


class FeedUnitOfWork(abstract.AbstractUnitOfWork):
    def __init__(
        self,
        database_name: str,
        post_repository: repository.PostRepository,
        friend_repository: repository.FriendRepository,
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

        self.posts = post_repository
        self.friends = friend_repository

    async def _init_repositories(
        self, session: typing.Optional[AsyncSession] = None
    ) -> None:
        self.posts(session)
        self.friends(session)
