import asyncio
import typing
import uuid

from social_network.domain import exceptions as domain_exceptions
from social_network.domain import models
from social_network.domain.services import abstract
from social_network.infrastructure.database import (
    exceptions as database_exceptions,
)
from social_network.infrastructure.database import (
    uow,
)


class FriendService(abstract.AbstractService):
    @property
    def uow(self) -> uow.FriendUnitOfWork:
        return typing.cast(uow.FriendUnitOfWork, self._uow)

    async def make_friendship(
        self, user: models.UserDomain, friend_id: uuid.UUID
    ) -> models.FriendDomain:
        async for _ in self.uow.transaction():
            try:
                friend, _ = await asyncio.gather(
                    self.uow.friends.create(
                        models.NewFriendDomain(
                            user_id=user.id,
                            friend_id=friend_id,
                        )
                    ),
                    self.uow.friends.create(
                        models.NewFriendDomain(
                            user_id=friend_id,
                            friend_id=user.id,
                        )
                    ),
                )
            except database_exceptions.RelatedObjectDoesNotExistError as err:
                raise domain_exceptions.FriendNotFoundError(
                    user_id=str(user.id), friend_id=str(friend_id)
                ) from err
        return friend

    async def delete_friendship(
        self, user: models.UserDomain, friend_id: uuid.UUID
    ) -> None:
        async for _ in self.uow.transaction():
            user_friends, friend_friends = await asyncio.gather(
                self.uow.friends.find_all(
                    filters={"user_id": user.id, "friend_id": friend_id},
                    exclude_deleted=True,
                ),
                self.uow.friends.find_all(
                    filters={"user_id": friend_id, "friend_id": user.id},
                    exclude_deleted=True,
                ),
            )
            if not user_friends:
                raise domain_exceptions.FriendNotFoundError(
                    user_id=str(user.id), friend_id=str(friend_id)
                )
            if not friend_friends:
                raise domain_exceptions.FriendNotFoundError(
                    user_id=str(friend_id), friend_id=str(user.id)
                )
            await asyncio.gather(
                self.uow.friends.delete(user_friends[0]),
                self.uow.friends.delete(friend_friends[0]),
            )
        return None
