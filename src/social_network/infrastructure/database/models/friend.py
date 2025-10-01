import uuid

import sqlalchemy.orm

from social_network.infrastructure.database.models import base, mixins, user


class FriendORM(mixins.CreatedAtUpdatedAtDeletedAtMixin, base.BaseORM):
    __tablename__ = "friends"

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
    friend_id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.ForeignKey(
            user.UserORM.id, onupdate="RESTRICT", ondelete="RESTRICT"
        ),
        nullable=False,
        index=True,
    )
