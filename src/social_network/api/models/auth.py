import uuid

import pydantic


class AuthDTO(pydantic.BaseModel):
    id: str = pydantic.Field(examples=[str(uuid.uuid4())])
    password: str = pydantic.Field(examples=["Секретная строка"])


class TokenDTO(pydantic.BaseModel):
    token: str = pydantic.Field(
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        ]
    )
