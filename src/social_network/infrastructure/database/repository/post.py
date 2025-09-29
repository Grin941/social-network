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


class PostRepository(
    abstract.AbstractRepository[
        models.PostDomain, models.NewPostDomain, models.UpdatingPostDomain, AsyncSession
    ],
    mixins.SelectPreparationMixin[orm.PostORM],
):
    @property
    def _create_statement(self) -> sqlalchemy.TextClause:
        return sqlalchemy.text(
            "INSERT INTO posts (id, author_id, text, created_at, updated_at, deleted_at) "
            "VALUES (:id, :author_id, :text, :created_at, :updated_at, :deleted_at)"
        )

    async def create(self, item: models.NewPostDomain) -> models.PostDomain:
        session = self._get_db_session()
        id_ = str(uuid.uuid4())
        try:
            await session.execute(
                self._create_statement,
                item.model_dump() | {"id": id_},
            )
        except sqlalchemy.exc.IntegrityError as err:
            raise exceptions.RelatedObjectDoesNotExistError(
                model="posts", fk_model="author", fk_value=item.author_id
            ) from err

        return await self.find_one(id_)

    async def batch_create(
        self, items: list[models.NewPostDomain]
    ) -> list[models.PostDomain]:
        session = self._get_db_session()
        insert_posts = [item.model_dump() | {"id": str(uuid.uuid4())} for item in items]
        await session.execute(self._create_statement, insert_posts)

        posts = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.PostORM,
                        where_clause=f"id IN ({', '.join((f"'{item['''id''']}'" for item in insert_posts))})",
                    )
                )
            )
            .mappings()
            .all()
        )
        return [models.PostDomain(**post) for post in posts]

    async def find_one(self, id_: str) -> models.PostDomain:
        posts = await self.find_all(filters={"id": id_})
        if not posts:
            raise exceptions.ObjectDoesNotExistError(model="posts", id_=id_)
        return posts[0]

    async def find_all(
        self,
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.PostDomain]:
        session = self._get_db_session()
        posts = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.PostORM,
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
        return [models.PostDomain(**post) for post in posts]

    async def update(self, item: models.UpdatingPostDomain) -> models.PostDomain:
        session = self._get_db_session()
        await session.execute(
            sqlalchemy.text(
                "UPDATE posts "
                "SET author_id = :author_id, text = :text, updated_at = :updated_at, deleted_at = :deleted_at "
                "WHERE id = :id"
            ),
            item.model_dump(),
        )
        return await self.find_one(str(item.id))

    async def delete(self, item: models.PostDomain) -> None:
        item.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        await self.update(models.UpdatingPostDomain(**item.model_dump()))

    async def batch_delete(self, items: typing.List[models.PostDomain]) -> None:
        raise NotImplementedError()

    async def feed(
        self, user_id: uuid.UUID, offset: int, limit: int
    ) -> list[models.PostDomain]:
        session = self._get_db_session()
        posts = (
            (
                await session.execute(
                    sqlalchemy.text(
                        "SELECT p.* "
                        "FROM posts p JOIN friends f "
                        "ON ((p.author_id = f.user_id AND f.friend_id = :current_user_id) "
                        "OR (p.author_id = f.friend_id AND f.user_id = :current_user_id)) "
                        "WHERE p.author_id != :current_user_id "
                        "AND p.deleted_at IS NULL "
                        "AND f.deleted_at IS NULL "
                        "OFFSET :offset "
                        "LIMIT :limit"
                    ),
                    {"current_user_id": str(user_id), "offset": offset, "limit": limit},
                )
            )
            .mappings()
            .all()
        )
        return [models.PostDomain(**post) for post in posts]
