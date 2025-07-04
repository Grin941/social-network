import typing
import uuid

from social_network.database.repository import abstract_repository
from social_network.database import exceptions
from social_network.domain import models

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(
    abstract_repository.AbstractRepository[
        models.NewUserDomain, models.UserDomain, AsyncSession
    ]
):
    async def create(self, item: models.NewUserDomain) -> models.UserDomain:
        session = self._get_db_session()
        id_ = str(uuid.uuid4())
        await session.execute(
            sqlalchemy.text(
                "INSERT INTO users (id, first_name, second_name, birthdate, biography, city, password) "
                "VALUES (:id, :first_name, :second_name, :birthdate, :biography, :city, :password)"
            ),
            item.model_dump() | {"id": id_},
        )

        return await self.find_one(id_)

    async def find_one(self, id_: str) -> models.UserDomain:
        session = self._get_db_session()
        users = await session.execute(
            sqlalchemy.text(f"SELECT * from users where id = '{id_}'")
        )
        for user in users.mappings().all():
            return models.UserDomain(**user)

        raise exceptions.ObjectDoesNotExistError(model="users", id_=id_)

    async def find_all(self, filters: dict[str, typing.Any]) -> list[models.UserDomain]:
        session = self._get_db_session()
        users = await session.execute(
            sqlalchemy.text(
                f"SELECT * from users where {' AND '.join([f"""{k} = '{str(v)}'""" for k, v in filters.items()])}"
            )
        )
        return [models.UserDomain(**user) for user in users.mappings().all()]
