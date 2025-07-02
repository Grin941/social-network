import pydantic
import enum
import datetime

from cryptography import fernet


class SexEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class PasswordMixin:
    @staticmethod
    def encrypt_password(password: str, secret: str) -> str:
        return fernet.Fernet(secret).encrypt(password.encode()).decode()

    @staticmethod
    def decrypt_password(password: str, secret: str) -> str:
        return fernet.Fernet(secret).decrypt(password).decode()


class NewUserDomain(PasswordMixin, pydantic.BaseModel):
    first_name: str
    second_name: str
    birdth_date: datetime.datetime
    biography: str
    city: str
    sex: SexEnum
    password: str


class UserDomain(NewUserDomain):
    id: int
