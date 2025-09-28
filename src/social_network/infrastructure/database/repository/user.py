import typing
import uuid

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from social_network.domain import models
from social_network.infrastructure.database import exceptions
from social_network.infrastructure.database import models as orm
from social_network.infrastructure.database.repository import abstract, mixins


class UserRepository(
    abstract.AbstractRepository[
        models.UserDomain, models.NewUserDomain, models.UserDomain, AsyncSession
    ],
    mixins.SelectPreparationMixin[orm.UserORM],
):
    @property
    def _create_statement(self) -> sqlalchemy.TextClause:
        return sqlalchemy.text(
            "INSERT INTO users (id, first_name, second_name, birthdate, biography, city, password, created_at, updated_at, deleted_at) "
            "VALUES (:id, :first_name, :second_name, :birthdate, :biography, :city, :password, :created_at, :updated_at, :deleted_at)"
        )

    async def create(self, item: models.NewUserDomain) -> models.UserDomain:
        session = self._get_db_session()
        id_ = str(uuid.uuid4())
        await session.execute(
            self._create_statement,
            item.model_dump() | {"id": id_},
        )

        return await self.find_one(id_)

    async def batch_create(self, items: typing.List[models.NewUserDomain]) -> None:
        session = self._get_db_session()
        await session.execute(
            self._create_statement,
            [item.model_dump() | {"id": str(uuid.uuid4())} for item in items],
        )

    async def search(
        self, first_name_prefix: str, second_name_prefix: str
    ) -> list[models.UserDomain]:
        session = self._get_db_session()
        users = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.UserORM,
                        where_clause=f"second_name LIKE '{second_name_prefix}%' AND first_name LIKE '{first_name_prefix}%'",
                        exclude_deleted=True,
                        order_by="created_at desc",
                    )
                )
            )
            .mappings()
            .all()
        )
        return [models.UserDomain(**user) for user in users]

    async def find_one(self, id_: str) -> models.UserDomain:
        users = await self.find_all(filters={"id": id_})
        if not users:
            raise exceptions.ObjectDoesNotExistError(model="users", id_=id_)
        return users[0]

    async def find_all(
        self,
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.UserDomain]:
        session = self._get_db_session()
        users = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.UserORM,
                        filters=filters,
                        order_by=order_by,
                        limit=limit,
                        exclude_deleted=exclude_deleted,
                    )
                )
            )
            .mappings()
            .all()
        )
        return [models.UserDomain(**user) for user in users]

    async def update(self, item: models.UserDomain) -> models.UserDomain:
        raise NotImplementedError()

    async def delete(self, item: models.UserDomain) -> None:
        raise NotImplementedError()

    async def batch_delete(self, items: typing.List[models.UserDomain]) -> None:
        raise NotImplementedError()
