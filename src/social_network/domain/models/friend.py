import uuid

import pydantic

from social_network.domain import mixins


class NewFriendDomain(
    mixins.ModelWithCreatedAtUpdatedAtDeletedAtMixin, pydantic.BaseModel
):
    user_id: uuid.UUID
    friend_id: uuid.UUID


class FriendDomain(NewFriendDomain):
    id: uuid.UUID
