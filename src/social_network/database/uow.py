import typing
import types

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from social_network.database import exceptions, repository


class UnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        user_repository: repository.UserRepository,
    ) -> None:
        self._session_factory = session_factory
        self._session: typing.Optional[AsyncSession] = None

        self.users = user_repository

    async def _init_repositories(
        self, session: typing.Optional[AsyncSession] = None
    ) -> None:
        self.users(session)

    async def __aenter__(self) -> None:
        session = self._session_factory()
        await self._init_repositories(session)
        self._session = session

    async def __aexit__(
        self,
        exc_type: typing.Optional[type[BaseExceptionGroup]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType],
    ) -> None:
        session = typing.cast(AsyncSession, self._session)
        try:
            if exc_type:
                try:
                    await session.rollback()
                except Exception as exc:
                    raise exceptions.DatabaseError(repr(exc)) from exc
            else:
                try:
                    await session.commit()
                except Exception as exc:
                    raise exceptions.DatabaseError(repr(exc)) from exc
        finally:
            await session.close()
            self._session = None
            await self._init_repositories()

    def transaction(self) -> "UnitOfWork":
        return self
