import types
import typing

import pytest
import pytest_mock

from social_network.infrastructure.database import uow
from social_network.infrastructure.database.repository import user_repository


class UnitOfWorkMock(uow.UnitOfWork):
    async def __aenter__(self) -> None:
        return None

    async def __aexit__(
        self,
        exc_type: typing.Optional[type[BaseExceptionGroup]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType],
    ) -> None:
        return None


@pytest.fixture
def unit_of_work(mocker: pytest_mock.MockerFixture) -> uow.UnitOfWork:
    return UnitOfWorkMock(
        session_factory=mocker.AsyncMock(),
        user_repository=user_repository.UserRepository(),
    )
