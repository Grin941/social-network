import pydantic

from social_network.api.models import user


class RegistrationDTO(user._UserDTO):
    password: str


class NewUserDTO(pydantic.BaseModel):
    user_id: str
