import typing
import uuid

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from social_network.domain import models
from social_network.infrastructure.database import exceptions
from social_network.infrastructure.database.repository import abstract_repository


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

    async def batch_create(self, items: typing.List[models.NewUserDomain]) -> None:
        session = self._get_db_session()
        await session.execute(
            sqlalchemy.text(
                "INSERT INTO users (id, first_name, second_name, birthdate, biography, city, password) "
                "VALUES (:id, :first_name, :second_name, :birthdate, :biography, :city, :password)"
            ),
            [item.model_dump() | {"id": str(uuid.uuid4())} for item in items],
        )

    async def search(
        self, first_name_prefix: str, second_name_prefix: str
    ) -> list[models.UserDomain]:
        session = self._get_db_session()
        users = await session.execute(
            sqlalchemy.text(
                f"SELECT * "
                f"FROM users "
                f"WHERE second_name LIKE '{second_name_prefix}%' AND first_name LIKE '{first_name_prefix}%' "
                f"ORDER BY id"
            )
        )
        return [models.UserDomain(**user) for user in users.mappings().all()]

    async def find_one(self, id_: str) -> models.UserDomain:
        session = self._get_db_session()
        users = await session.execute(
            sqlalchemy.text(f"SELECT * FROM users WHERE id = '{id_}'")
        )
        for user in users.mappings().all():
            return models.UserDomain(**user)

        raise exceptions.ObjectDoesNotExistError(model="users", id_=id_)

    async def find_all(self, filters: dict[str, typing.Any]) -> list[models.UserDomain]:
        session = self._get_db_session()
        users = await session.execute(
            sqlalchemy.text(
                f"SELECT * FROM users WHERE {' AND '.join([f"""{k} = '{str(v)}'""" for k, v in filters.items()])}"
            )
        )
        return [models.UserDomain(**user) for user in users.mappings().all()]
