import datetime
import typing

import pydantic


class ModelWithCreatedAtUpdatedAtMixin:
    created_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        title="Date and time when the object was created",
    )
    updated_at: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        title="Date and time when the object was updated last time",
    )

    @pydantic.model_validator(mode="before")
    @classmethod
    def check_datetime(cls, data: typing.Any) -> typing.Any:
        if isinstance(data, dict):
            if "created_at" not in data:
                data["created_at"] = datetime.datetime.utcnow()
            if "updated_at" not in data:
                data["updated_at"] = data["created_at"]
        return data
