import uuid

import sqlalchemy.orm

from social_network.infrastructure.database.models import base, mixins, user


class PostORM(mixins.CreatedAtUpdatedAtDeletedAtMixin, base.BaseORM):
    __tablename__ = "posts"

    id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        primary_key=True, default=uuid.uuid4
    )
    author_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.ForeignKey(
            user.UserORM.id, onupdate="RESTRICT", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    text: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(sqlalchemy.TEXT())
