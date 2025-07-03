import datetime
import uuid

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.dialects.postgresql import UUID

from src.social_network.infrastructure.database.orm import base_orm


class UserORM(base_orm.BaseORM):
    __tablename__ = "users"

    id: sqlalchemy.orm.Mapped[uuid.UUID] = sqlalchemy.orm.mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False
    )
    first_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        nullable=False
    )
    second_name: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        nullable=False
    )
    birdth_date: sqlalchemy.orm.Mapped[datetime.datetime] = (
        sqlalchemy.orm.mapped_column(nullable=False)
    )
    biography: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        sqlalchemy.Text, nullable=False
    )
    city: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(nullable=False)
    sex: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(nullable=False)
    password: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(nullable=False)
