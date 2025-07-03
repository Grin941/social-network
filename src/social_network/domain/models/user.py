import pydantic
import datetime


class NewUserDomain(pydantic.BaseModel):
    first_name: str
    second_name: str
    birdth_date: datetime.datetime
    biography: str
    city: str
    password: str


class UserDomain(NewUserDomain):
    id: str
