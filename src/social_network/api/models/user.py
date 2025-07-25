import typing
import uuid

import pydantic
import datetime


def _now() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


class _UserDTO(pydantic.BaseModel):
    first_name: str = pydantic.Field(default_factory=str, examples=["Имя"])
    second_name: str = pydantic.Field(default_factory=str, examples=["Фамилия"])
    birthdate: datetime.date = pydantic.Field(default_factory=_now, examples=[_now()])
    biography: str = pydantic.Field(
        default_factory=str, examples=["Хобби, интересы и т.п."]
    )
    city: str = pydantic.Field(default_factory=str, examples=["Москва"])

    @pydantic.field_validator("birthdate", mode="before")
    @classmethod
    def validate_birthdate(cls, v: typing.Any) -> datetime.date:
        if isinstance(v, datetime.datetime):
            return v.date()
        elif isinstance(v, datetime.date):
            return v
        else:
            raise ValueError("invalid birthdate")


class UserDTO(_UserDTO):
    id: str = pydantic.Field(examples=[str(uuid.uuid4())])
