import typing
import uuid

import sqlalchemy.orm

from social_network.infrastructure.database.models import base, mixins, user


class ChatORM(mixins.CreatedAtUpdatedAtDeletedAtMixin, base.BaseORM):
    __tablename__ = "chats"

    id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        primary_key=True, default=uuid.uuid4
    )
    name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(nullable=False)
    owner_id: sqlalchemy.orm.Mapped[typing.Optional[uuid.UUID]] = (
        sqlalchemy.orm.MappedColumn(
            sqlalchemy.ForeignKey(
                user.UserORM.id, onupdate="RESTRICT", ondelete="RESTRICT"
            ),
            index=False,
            nullable=True,
            default=None,
        )
    )


class ChatParticipantORM(mixins.CreatedAtUpdatedAtDeletedAtMixin, base.BaseORM):
    __tablename__ = "chat_participants"

    id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        primary_key=True, default=uuid.uuid4
    )
    user_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.ForeignKey(
            user.UserORM.id, onupdate="RESTRICT", ondelete="RESTRICT"
        ),
        nullable=False,
        index=True,
    )
    chat_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.ForeignKey(ChatORM.id, onupdate="RESTRICT", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )


class ChatMessageORM(mixins.CreatedAtUpdatedAtDeletedAtMixin, base.BaseORM):
    __tablename__ = "chat_messages"

    id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        primary_key=True, default=uuid.uuid4
    )
    author_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.ForeignKey(
            user.UserORM.id, onupdate="RESTRICT", ondelete="RESTRICT"
        ),
        nullable=False,
        index=True,
    )
    chat_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.ForeignKey(ChatORM.id, onupdate="RESTRICT", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    text: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(nullable=False)
