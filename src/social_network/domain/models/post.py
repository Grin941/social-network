import datetime
import typing
import uuid

import pydantic

from social_network.domain import mixins


class NewPostDomain(
    mixins.ModelWithCreatedAtUpdatedAtDeletedAtMixin, pydantic.BaseModel
):
    author_id: uuid.UUID
    text: str


class PostDomain(NewPostDomain):
    id: uuid.UUID


class UpdatingPostDomain(pydantic.BaseModel):
    id: uuid.UUID
    text: str
    updated_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    deleted_at: typing.Optional[datetime.datetime] = None
