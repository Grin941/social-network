import pydantic
import datetime


class _UserDTO(pydantic.BaseModel):
    first_name: str
    second_name: str
    birthdate: datetime.datetime
    biography: str
    city: str


class UserDTO(_UserDTO):
    id: str
