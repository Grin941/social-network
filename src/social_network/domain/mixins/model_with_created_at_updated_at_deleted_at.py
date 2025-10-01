import datetime
import typing

import pydantic

from social_network.domain.mixins import model_with_created_at_updated_at


class ModelWithCreatedAtUpdatedAtDeletedAtMixin(
    model_with_created_at_updated_at.ModelWithCreatedAtUpdatedAtMixin
):
    deleted_at: typing.Optional[datetime.datetime] = pydantic.Field(
        default=None,
        title="Date and time when the object was deleted",
    )
