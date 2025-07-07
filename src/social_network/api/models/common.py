import uuid

import pydantic


class ErrorMessage(pydantic.BaseModel):
    message: str
    request_id: str = pydantic.Field(examples=[str(uuid.uuid4())])
    code: int = pydantic.Field(ge=0)
