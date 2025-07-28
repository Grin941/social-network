from social_network.domain.services import abstract

from social_network.domain import models, exceptions as domain_exceptions
from social_network.infrastructure.database import exceptions as database_exceptions


class UserService(abstract.AbstractService):
    async def get_user(self, id_: str) -> models.UserDomain:
        async for _ in self._uow.transaction():
            try:
                user = await self._uow.users.find_one(id_)
            except database_exceptions.ObjectDoesNotExistError as err:
                raise domain_exceptions.UserNotFoundError(id_) from err
        return user
