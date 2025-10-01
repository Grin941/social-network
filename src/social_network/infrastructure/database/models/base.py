from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncAttrs

from social_network.infrastructure.database.models import types


class BaseORM(AsyncAttrs, orm.DeclarativeBase):
    type_annotation_map = types.type_annotation_mapper
