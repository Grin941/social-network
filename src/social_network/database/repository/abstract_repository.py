import typing
import abc

from src.social_network.database import exceptions


Entity = typing.TypeVar("Entity")
NewEntity = typing.TypeVar("NewEntity")
DBSessionType = typing.TypeVar("DBSessionType")


class AbstractRepository(abc.ABC, typing.Generic[Entity, NewEntity, DBSessionType]):
    def __init__(self) -> None:
        self._db_session = None

    def __call__(
        self, db_session: typing.Optional[DBSessionType] = None
    ) -> "AbstractRepository[Entity, NewEntity, DBSessionType]":
        self._db_session = db_session
        return self

    def _get_db_session(self) -> DBSessionType:
        if not self._db_session:
            raise exceptions.NoSessionError("Session not found")
        return self._db_session

    @abc.abstractmethod
    async def create(self, item: NewEntity) -> Entity: ...

    @abc.abstractmethod
    async def find_one(self, id_: typing.Any) -> Entity: ...
