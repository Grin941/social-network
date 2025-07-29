import asyncio
import logging
import types
import typing

import sqlalchemy
from sqlalchemy import exc as sa_exc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from social_network.infrastructure.database import exceptions, repository, retry

MAX_CONNECTION_ATTEMPTS: int = 3
PAUSE_BETWEEN_ATTEMPTS_SECONDS: float = 0.1


logger = logging.getLogger(__name__)


def database_connection_exception_handler(_: BaseException) -> bool:
    return False


def get_typical_db_exceptions_handlers(
    extra_handlers: typing.Optional[retry.ExceptionHandlers] = None,
) -> retry.ExceptionHandlers:
    return {
        sa_exc.InterfaceError: database_connection_exception_handler,
        sa_exc.InternalError: database_connection_exception_handler,
        sa_exc.OperationalError: database_connection_exception_handler,
        exceptions.DatabaseError: database_connection_exception_handler,
    } | (extra_handlers or {})


class UnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        user_repository: repository.UserRepository,
        timeout_seconds: int = 0,
    ) -> None:
        self._session_factory = session_factory
        self._session: typing.Optional[AsyncSession] = None
        self._timeout_seconds = timeout_seconds

        self.users = user_repository

    async def __aenter__(self) -> "UnitOfWork":
        checking_connection_attempts = MAX_CONNECTION_ATTEMPTS
        session_is_valid: bool = False
        while not session_is_valid and checking_connection_attempts > 0:
            session = self._session_factory()
            try:
                if self._timeout_seconds > 0:
                    await session.execute(
                        sqlalchemy.text(
                            f"SET STATEMENT_TIMEOUT={self._timeout_seconds}s"
                        )
                    )
                await self._init_repositories(session)
                self._session = session
                session_is_valid = True
            except (sa_exc.OperationalError, sa_exc.TimeoutError) as exc:
                logger.debug(
                    f"Attempt to get session was unsuccessful. "
                    f"Attempts left: {checking_connection_attempts}. Error: {exc}"
                )
                checking_connection_attempts -= 1
                await session.close()
                if not checking_connection_attempts:
                    raise exceptions.SessionCreationError(
                        f"Exceed {MAX_CONNECTION_ATTEMPTS} db connection attempts"
                    ) from exc
                await asyncio.sleep(PAUSE_BETWEEN_ATTEMPTS_SECONDS)
        if session_is_valid:
            logger.debug("Unit of work started")

        return self

    async def _init_repositories(
        self, session: typing.Optional[AsyncSession] = None
    ) -> None:
        self.users(session)

    async def __aexit__(
        self,
        exc_type: typing.Optional[type[BaseExceptionGroup]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType],
    ) -> None:
        session = typing.cast(AsyncSession, self._session)
        try:
            if exc_type:
                logger.debug("Unit of work finished with error")
                try:
                    await session.rollback()
                except Exception as exc:
                    logger.debug("Error while rollback occurred")
                    raise exceptions.DatabaseError(repr(exc)) from exc
            else:
                logger.debug("Unit of work finished successfully")
                try:
                    await session.commit()
                except Exception as exc:
                    logger.debug("Error while commit occurred")
                    raise exceptions.DatabaseError(repr(exc)) from exc
        finally:
            await session.close()
            self._session = None
            await self._init_repositories()

    async def transaction(self) -> typing.AsyncIterator["UnitOfWork"]:
        async for attempt in retry.aretry(
            exceptions_handlers=get_typical_db_exceptions_handlers()
        ):
            with attempt:
                async with self as transaction:
                    yield transaction

    async def execute_raw_query(
        self, query: str, params: typing.Optional[dict[str, typing.Any]] = None
    ) -> sqlalchemy.Result[typing.Any]:
        if not self._session:
            raise exceptions.NoSessionError("No session found")

        return await self._session.execute(sqlalchemy.text(query), params)
