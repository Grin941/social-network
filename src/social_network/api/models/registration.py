import uuid

import pydantic

from social_network.api.models import user


class RegistrationDTO(user._UserDTO):
    password: str = pydantic.Field(examples=["Секретная строка"])


class NewUserDTO(pydantic.BaseModel):
    user_id: str = pydantic.Field(examples=[str(uuid.uuid4())])
