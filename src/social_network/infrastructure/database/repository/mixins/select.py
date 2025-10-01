import typing
from typing import Generic, Optional, TypeVar

import sqlalchemy

from social_network.infrastructure.database import models

ModelInSelectType = TypeVar("ModelInSelectType", bound=models.BaseORM)


class SelectPreparationMixin(Generic[ModelInSelectType]):
    @staticmethod
    def prepare_select(
        model_class: type[ModelInSelectType],
        *,
        select_fields: typing.Optional[str] = None,
        where_clause: typing.Optional[str] = None,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        exclude_deleted: bool = False,
        order_by: typing.Optional[str] = None,
        limit: Optional[int] = None,
    ) -> sqlalchemy.TextClause:
        query = f"SELECT {select_fields or '*'} FROM {model_class.__tablename__}"
        if where_clause:
            if exclude_deleted:
                where_clause += " AND deleted_at IS NULL"
            query += f" WHERE {where_clause}"
        elif filters:
            query += f" WHERE {' AND '.join([f"""{k} = '{str(v)}'""" for k, v in filters.items()])}"
            if exclude_deleted:
                query += " AND deleted_at IS NULL"
        elif exclude_deleted:
            query += " WHERE deleted_at IS NULL"

        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        return sqlalchemy.text(query)
