import datetime
import uuid

import sqlalchemy.orm

from social_network.infrastructure.database.models import base, mixins


class UserORM(mixins.CreatedAtUpdatedAtDeletedAtMixin, base.BaseORM):
    __tablename__ = "users"

    id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.MappedColumn(
        primary_key=True, default=uuid.uuid4
    )
    first_name: sqlalchemy.orm.Mapped[str]
    second_name: sqlalchemy.orm.Mapped[str]
    birthdate: sqlalchemy.orm.Mapped[datetime.datetime]
    biography: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.TEXT()
    )
    city: sqlalchemy.orm.Mapped[str]
    password: sqlalchemy.orm.Mapped[str]

    __table_args__ = (
        sqlalchemy.Index(
            "first_name_gin_idx",
            "first_name",
            postgresql_using="gin",
            postgresql_ops={"first_name": "gin_trgm_ops"},
        ),
        sqlalchemy.Index(
            "second_name_gin_idx",
            "second_name",
            postgresql_using="gin",
            postgresql_ops={"second_name": "gin_trgm_ops"},
        ),
    )
