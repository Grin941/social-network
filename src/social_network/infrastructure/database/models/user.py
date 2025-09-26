import datetime

import sqlalchemy.orm
from sqlalchemy.ext.asyncio import AsyncAttrs

from social_network.infrastructure.database.models import base


class UserORM(AsyncAttrs, base.BaseORM):
    __tablename__ = "users"

    id: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.VARCHAR(36), primary_key=True
    )
    first_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.VARCHAR(256)
    )
    second_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.VARCHAR(256)
    )
    birthdate: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.DateTime(timezone=True)
    )
    biography: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.TEXT()
    )
    city: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.VARCHAR(256)
    )
    password: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.MappedColumn(
        sqlalchemy.VARCHAR(256)
    )

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
