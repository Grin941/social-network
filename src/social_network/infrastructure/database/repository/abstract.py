import abc
import typing

from social_network.infrastructure.database import exceptions

Entity = typing.TypeVar("Entity")
NewEntity = typing.TypeVar("NewEntity")
UpdatingEntity = typing.TypeVar("UpdatingEntity")
DBSessionType = typing.TypeVar("DBSessionType")


class AbstractRepository(
    abc.ABC, typing.Generic[Entity, NewEntity, UpdatingEntity, DBSessionType]
):
    def __init__(self) -> None:
        self._db_session: typing.Optional[DBSessionType] = None

    def __call__(
        self, db_session: typing.Optional[DBSessionType] = None
    ) -> "AbstractRepository[Entity, NewEntity, UpdatingEntity, DBSessionType]":
        self._db_session = db_session
        return self

    def _get_db_session(self) -> DBSessionType:
        if not self._db_session:
            raise exceptions.NoSessionError("Session not found")
        return self._db_session

    @abc.abstractmethod
    async def create(self, item: NewEntity) -> Entity: ...

    @abc.abstractmethod
    async def update(self, item: UpdatingEntity) -> Entity: ...

    @abc.abstractmethod
    async def delete(self, item: Entity) -> None: ...

    @abc.abstractmethod
    async def find_all(
        self,
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[Entity]: ...

    @abc.abstractmethod
    async def find_one(self, id_: typing.Any) -> Entity: ...

    @abc.abstractmethod
    async def batch_create(self, items: list[NewEntity]) -> list[Entity]: ...

    @abc.abstractmethod
    async def batch_delete(self, items: list[Entity]) -> None: ...
