from social_network.domain.services import abstract

from social_network.domain.models.user import UserDomain


class UserService(abstract.AbstractService):
    async def get_user(self, id_: str) -> UserDomain:
        async with self._uow.transaction():
            return await self._uow.users.find_one(id_)
