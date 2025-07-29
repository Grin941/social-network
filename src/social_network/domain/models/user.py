import datetime

import pydantic


class NewUserDomain(pydantic.BaseModel):
    first_name: str
    second_name: str
    birthdate: datetime.datetime
    biography: str
    city: str
    password: str


class UserDomain(NewUserDomain):
    id: str
