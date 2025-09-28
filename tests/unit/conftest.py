import types
import typing

import pytest
import pytest_mock

from social_network.infrastructure.database import repository, uow


class UnitOfWorkMockMixin:
    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[type[BaseExceptionGroup]],
        exc_value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType],
    ) -> None:
        return None


@pytest.fixture
def database_name() -> str:
    return "socialnetwork"


@pytest.fixture
def user_unit_of_work(
    mocker: pytest_mock.MockerFixture, database_name: str
) -> uow.UserUnitOfWork:
    class UserUnitOfWork(UnitOfWorkMockMixin, uow.UserUnitOfWork): ...

    return UserUnitOfWork(
        database_name=database_name,
        master_factory=mocker.AsyncMock(),
        user_repository=repository.UserRepository(),
    )


@pytest.fixture
def friend_unit_of_work(
    mocker: pytest_mock.MockerFixture, database_name: str
) -> uow.FriendUnitOfWork:
    class FriendUnitOfWork(UnitOfWorkMockMixin, uow.FriendUnitOfWork): ...

    return FriendUnitOfWork(
        database_name=database_name,
        master_factory=mocker.AsyncMock(),
        friend_repository=repository.FriendRepository(),
    )


@pytest.fixture
def post_unit_of_work(
    mocker: pytest_mock.MockerFixture, database_name: str
) -> uow.PostUnitOfWork:
    class PostUnitOfWork(UnitOfWorkMockMixin, uow.PostUnitOfWork): ...

    return PostUnitOfWork(
        database_name=database_name,
        master_factory=mocker.AsyncMock(),
        post_repository=repository.PostRepository(),
    )
