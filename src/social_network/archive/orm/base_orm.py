import typing
import datetime

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import AsyncAttrs


type_annotation_mapper: dict[type, typing.Any] = {
    str: sqlalchemy.String(255),
    datetime.datetime: sqlalchemy.DateTime(timezone=True),
}


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class BaseORM(AsyncAttrs, sqlalchemy.orm.DeclarativeBase):
    type_annotation_map = type_annotation_mapper
    metadata = sqlalchemy.MetaData(naming_convention=NAMING_CONVENTION)

    # id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.MappedColumn(
    #     sqlalchemy.BigInteger, sqlalchemy.Identity(always=True), primary_key=True
    # )

    def model_dump(self) -> dict[str, typing.Any]:
        d = {}
        for column in self.__table__.columns.keys():
            d[column] = getattr(self, column)
        return d

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.id=}"
