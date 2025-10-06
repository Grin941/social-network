import typing
import uuid

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy.ext.asyncio import AsyncSession

from social_network.domain import models
from social_network.infrastructure.database import exceptions
from social_network.infrastructure.database import models as orm
from social_network.infrastructure.database.repository import abstract, mixins


class ChatRepository(
    abstract.AbstractRepository[
        models.ChatDomain, models.NewChatDomain, models.ChatDomain, AsyncSession
    ],
    mixins.SelectPreparationMixin[orm.ChatORM],
):
    @property
    def _create_statement(self) -> sqlalchemy.TextClause:
        return sqlalchemy.text(
            "INSERT INTO chats (id, name, owner_id, created_at, updated_at, deleted_at) "
            "VALUES (:id, :name, :owner_id, :created_at, :updated_at, :deleted_at)"
        )

    async def create(self, item: models.NewChatDomain) -> models.ChatDomain:
        session = self._get_db_session()
        id_ = str(uuid.uuid4())
        await session.execute(
            self._create_statement,
            item.model_dump() | {"id": id_},
        )

        return await self.find_one(id_)

    async def batch_create(
        self, items: list[models.NewChatDomain]
    ) -> list[models.ChatDomain]:
        session = self._get_db_session()
        insert_items = [item.model_dump() | {"id": str(uuid.uuid4())} for item in items]
        await session.execute(self._create_statement, insert_items)

        chats = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.ChatORM,
                        where_clause=f"id IN ({', '.join((f"'{item['''id''']}'" for item in insert_items))})",
                    )
                )
            )
            .mappings()
            .all()
        )
        return [models.ChatDomain(**chat) for chat in chats]

    async def find_one(self, id_: str) -> models.ChatDomain:
        chats = await self.find_all(filters={"id": id_})
        if not chats:
            raise exceptions.ObjectDoesNotExistError(model="chats", id_=id_)
        return chats[0]

    async def find_dialog_id(
        self, user_id: str, friend_id: str
    ) -> typing.Optional[uuid.UUID]:
        session = self._get_db_session()
        result = await session.execute(
            sqlalchemy.text(
                f"""
                SELECT chat_id
                FROM chat_participants
                WHERE user_id IN ('{user_id}', '{friend_id}')
                GROUP BY chat_id
                HAVING COUNT(*) = 2;
                """
            )
        )
        try:
            return result.scalar_one()
        except sqlalchemy.exc.NoResultFound:
            return None

    async def find_all(
        self,
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.ChatDomain]:
        session = self._get_db_session()
        chats = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.ChatORM,
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
        return [models.ChatDomain(**chat) for chat in chats]

    async def update(self, item: models.ChatDomain) -> models.ChatDomain:
        raise NotImplementedError()

    async def delete(self, item: models.ChatDomain) -> None:
        raise NotImplementedError()

    async def batch_delete(self, items: typing.List[models.ChatDomain]) -> None:
        raise NotImplementedError()


class ChatParticipantRepository(
    abstract.AbstractRepository[
        models.ChatParticipantDomain,
        models.NewChatParticipantDomain,
        models.ChatParticipantDomain,
        AsyncSession,
    ],
    mixins.SelectPreparationMixin[orm.ChatParticipantORM],
):
    @property
    def _create_statement(self) -> sqlalchemy.TextClause:
        return sqlalchemy.text(
            "INSERT INTO chat_participants (id, user_id, chat_id, created_at, updated_at, deleted_at) "
            "VALUES (:id, :user_id, :chat_id, :created_at, :updated_at, :deleted_at)"
        )

    async def create(
        self, item: models.NewChatParticipantDomain
    ) -> models.ChatParticipantDomain:
        session = self._get_db_session()
        id_ = str(uuid.uuid4())
        await session.execute(
            self._create_statement,
            item.model_dump() | {"id": id_},
        )

        return await self.find_one(id_)

    async def batch_create(
        self, items: list[models.NewChatParticipantDomain]
    ) -> list[models.ChatParticipantDomain]:
        session = self._get_db_session()
        insert_items = [item.model_dump() | {"id": str(uuid.uuid4())} for item in items]
        await session.execute(self._create_statement, insert_items)

        participants = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.ChatParticipantORM,
                        where_clause=f"id IN ({', '.join((f"'{item['''id''']}'" for item in insert_items))})",
                    )
                )
            )
            .mappings()
            .all()
        )
        return [
            models.ChatParticipantDomain(**participant) for participant in participants
        ]

    async def find_one(self, id_: str) -> models.ChatParticipantDomain:
        participants = await self.find_all(filters={"id": id_})
        if not participants:
            raise exceptions.ObjectDoesNotExistError(model="chat_participants", id_=id_)
        return participants[0]

    async def find_all(
        self,
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.ChatParticipantDomain]:
        session = self._get_db_session()
        participants = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.ChatParticipantORM,
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
        return [
            models.ChatParticipantDomain(**participant) for participant in participants
        ]

    async def update(
        self, item: models.ChatParticipantDomain
    ) -> models.ChatParticipantDomain:
        raise NotImplementedError()

    async def delete(self, item: models.ChatParticipantDomain) -> None:
        raise NotImplementedError()

    async def batch_delete(
        self, items: typing.List[models.ChatParticipantDomain]
    ) -> None:
        raise NotImplementedError()


class ChatMessageRepository(
    abstract.AbstractRepository[
        models.ChatMessageDomain,
        models.NewChatMessageDomain,
        models.ChatMessageDomain,
        AsyncSession,
    ],
    mixins.SelectPreparationMixin[orm.ChatMessageORM],
):
    @property
    def _create_statement(self) -> sqlalchemy.TextClause:
        return sqlalchemy.text(
            "INSERT INTO chat_messages (id, author_id, chat_id, text, created_at, updated_at, deleted_at) "
            "VALUES (:id, :author_id, :chat_id, :text, :created_at, :updated_at, :deleted_at)"
        )

    async def create(
        self, item: models.NewChatMessageDomain
    ) -> models.ChatMessageDomain:
        session = self._get_db_session()
        id_ = str(uuid.uuid4())
        await session.execute(
            self._create_statement,
            item.model_dump() | {"id": id_},
        )

        return await self.find_one(id_)

    async def batch_create(
        self, items: list[models.NewChatMessageDomain]
    ) -> list[models.ChatMessageDomain]:
        session = self._get_db_session()
        insert_items = [item.model_dump() | {"id": str(uuid.uuid4())} for item in items]
        await session.execute(self._create_statement, insert_items)

        messages = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.ChatMessageORM,
                        where_clause=f"id IN ({', '.join((f"'{item['''id''']}'" for item in insert_items))})",
                    )
                )
            )
            .mappings()
            .all()
        )
        return [models.ChatMessageDomain(**message) for message in messages]

    async def find_one(self, id_: str) -> models.ChatMessageDomain:
        messages = await self.find_all(filters={"id": id_})
        if not messages:
            raise exceptions.ObjectDoesNotExistError(model="chat_messages", id_=id_)
        return messages[0]

    async def find_all(
        self,
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.ChatMessageDomain]:
        session = self._get_db_session()
        messages = (
            (
                await session.execute(
                    self.prepare_select(
                        model_class=orm.ChatMessageORM,
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
        return [models.ChatMessageDomain(**message) for message in messages]

    async def update(self, item: models.ChatMessageDomain) -> models.ChatMessageDomain:
        raise NotImplementedError()

    async def delete(self, item: models.ChatMessageDomain) -> None:
        raise NotImplementedError()

    async def batch_delete(self, items: typing.List[models.ChatMessageDomain]) -> None:
        raise NotImplementedError()
