import pydantic


class AuthDTO(pydantic.BaseModel):
    id: str
    password: str


class TokenDTO(pydantic.BaseModel):
    token: str
