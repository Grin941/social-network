import datetime
import uuid

import pydantic

from social_network.domain import mixins


class NewUserDomain(
    mixins.ModelWithCreatedAtUpdatedAtDeletedAtMixin, pydantic.BaseModel
):
    first_name: str
    second_name: str
    birthdate: datetime.datetime
    biography: str
    city: str
    password: str


class UserDomain(NewUserDomain):
    id: uuid.UUID
