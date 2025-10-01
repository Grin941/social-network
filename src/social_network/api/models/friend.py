import datetime
import uuid

import pydantic


class FriendDTO(pydantic.BaseModel):
    user_id: uuid.UUID = pydantic.Field(examples=[uuid.uuid4()])
    friend_id: uuid.UUID = pydantic.Field(examples=[uuid.uuid4()])
    created_at: datetime.datetime = pydantic.Field(
        examples=[datetime.datetime.now(datetime.timezone.utc)]
    )
