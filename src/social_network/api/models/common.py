import pydantic


class ErrorMessage(pydantic.BaseModel):
    message: str
    request_id: str
    code: int
