import datetime
import typing

import sqlalchemy.orm


class CreatedAtUpdatedAtMixin:
    created_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.MappedColumn(
        nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at: sqlalchemy.orm.Mapped[datetime.datetime] = sqlalchemy.orm.MappedColumn(
        nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class CreatedAtUpdatedAtDeletedAtMixin(CreatedAtUpdatedAtMixin):
    deleted_at: sqlalchemy.orm.Mapped[typing.Optional[datetime.datetime]] = (
        sqlalchemy.orm.MappedColumn(nullable=True, default=None)
    )
