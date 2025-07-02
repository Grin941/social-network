from src.social_network.database.repository import abstract_repository
from src.social_network.database import exceptions
from src.social_network import domain

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(abstract_repository.AbstractRepository[domain.NewUserDomain, domain.UserDomain, AsyncSession]):
    async def create(self, item: domain.NewUserDomain) -> domain.UserDomain:
        session = self._get_db_session()
        result = await session.execute(
            sqlalchemy.text(
                f"INSERT INTO users (first_name, second_name, birdth_date, biography, city, sex, password) "
                f"VALUES (:first_name, :second_name, :birdth_date, :biography, :city, :sex, :password)"
            ),
            **item.model_dump(),
        )

        user_id = result.inserted_primary_key.id
        return await self.find_one(user_id)

    async def find_one(self, id_: int) -> domain.UserDomain:
        session = self._get_db_session()
        users = await session.execute(
            sqlalchemy.text(f"SELECT * from users where id = {id_}")
        )
        for user in users:
            return domain.UserDomain(**user)

        raise exceptions.ObjectDoesNotExistError(model="users", id_=id_)
