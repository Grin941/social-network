import datetime
import typing
import uuid

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from social_network.domain import models
from social_network.infrastructure.database import exceptions
from social_network.infrastructure.database import models as orm
from social_network.infrastructure.database.repository import abstract, mixins


class FriendRepository(
    abstract.AbstractRepository[
        models.FriendDomain, models.NewFriendDomain, models.FriendDomain, AsyncSession
    ],
    mixins.SelectPreparationMixin[orm.FriendORM],
):
    @property
    def _create_statement(
        self,
    ) -> sqlalchemy.TextClause:
        return sqlalchemy.text(
            "INSERT INTO friends (id, user_id, friend_id, created_at, updated_at, deleted_at) "
            "VALUES (:id, :user_id, :friend_id, :created_at, :updated_at, :deleted_at)"
        )

    async def create(self, item: models.NewFriendDomain) -> models.FriendDomain:
        session = self._get_db_session()
        id_ = str(uuid.uuid4())
        try:
            await session.execute(
                self._create_statement,
                item.model_dump() | {"id": id_},
            )
        except sqlalchemy.exc.IntegrityError as err:
            raise exceptions.RelatedObjectDoesNotExistError(
                model="friends", fk_model="friend", fk_value=item.friend_id
            ) from err

        return await self.find_one(id_)

    async def batch_create(
        self, items: list[models.NewFriendDomain]
    ) -> list[models.FriendDomain]:
        session = self._get_db_session()
        insert_friends = [
            item.model_dump() | {"id": str(uuid.uuid4())} for item in items
        ]
        await session.execute(self._create_statement, insert_friends)

        friends = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.FriendORM,
                        where_clause=f"id IN ({', '.join((f"'{item['''id''']}'" for item in insert_friends))})",
                    )
                )
            )
            .mappings()
            .all()
        )
        return [models.FriendDomain(**friend) for friend in friends]

    async def find_one(self, id_: str) -> models.FriendDomain:
        friends = await self.find_all(filters={"id": id_})
        if not friends:
            raise exceptions.ObjectDoesNotExistError(model="friends", id_=id_)
        return friends[0]

    async def find_all(
        self,
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.FriendDomain]:
        session = self._get_db_session()
        friends = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.FriendORM,
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
        return [models.FriendDomain(**friend) for friend in friends]

    async def update(self, item: models.FriendDomain) -> models.FriendDomain:
        item.updated_at = datetime.datetime.now(datetime.timezone.utc)
        session = self._get_db_session()
        await session.execute(
            sqlalchemy.text(
                "UPDATE friends "
                "SET user_id = :user_id, friend_id = :friend_id, updated_at = :updated_at, deleted_at = :deleted_at "
                "WHERE id = :id"
            ),
            item.model_dump(),
        )
        return item

    async def delete(self, item: models.FriendDomain) -> None:
        item.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        await self.update(item)

    async def batch_delete(self, items: typing.List[models.FriendDomain]) -> None:
        raise NotImplementedError()
