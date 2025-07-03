import typing

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
    async def _find_duplicates(self, item: models.NewUserDomain) -> None:
        filters = {"password": item.password, "second_name": item.second_name}
        duplicates = await self.find_all(filters)
        if duplicates:
            raise exceptions.ObjectAlreadyExistsError(model="users", filters=filters)

    async def create(self, item: models.NewUserDomain) -> models.UserDomain:
        await self._find_duplicates(item)

        session = self._get_db_session()
        result = await session.execute(
            sqlalchemy.text(
                "INSERT INTO users (first_name, second_name, birdth_date, biography, city, sex, password) "
                "VALUES (:first_name, :second_name, :birdth_date, :biography, :city, :sex, :password)"
            ),
            **item.model_dump(),
        )

        # user_id = result.inserted_primary_key.id
        return await self.find_one(result.scalar_one())

    async def find_one(self, id_: str) -> models.UserDomain:
        session = self._get_db_session()
        users = await session.execute(
            sqlalchemy.text(f"SELECT * from users where id = {id_}")
        )
        for user in users.scalar_one():
            return models.UserDomain(**user)

        raise exceptions.ObjectDoesNotExistError(model="users", id_=id_)

    async def find_all(self, filters: dict[str, typing.Any]) -> list[models.UserDomain]:
        session = self._get_db_session()
        users = await session.execute(
            sqlalchemy.text(
                f"SELECT * from users where {' AND '.join([f"""{k} = '{v}'""" for k, v in filters.items()])}"
            )
        )
        return [models.UserDomain(**user) for user in users.scalars()]
