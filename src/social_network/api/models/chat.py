import uuid

import pydantic


class NewMessageDTO(pydantic.BaseModel):
    text: str = pydantic.Field(examples=["Привет, как дела?"])


class MessageDTO(NewMessageDTO):
    from_: uuid.UUID = pydantic.Field(examples=[uuid.uuid4()], alias="from")
    to: uuid.UUID = pydantic.Field(examples=[uuid.uuid4()])
