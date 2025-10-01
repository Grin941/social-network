import uuid

import pydantic


class NewPostDTO(pydantic.BaseModel):
    text: str = pydantic.Field(
        examples=[
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Lectus mauris ultrices eros in cursus turpis massa."
        ]
    )


class UpdatingPostDTO(NewPostDTO):
    id: uuid.UUID = pydantic.Field(examples=[uuid.uuid4()])


class PostDTO(UpdatingPostDTO):
    author_user_id: uuid.UUID = pydantic.Field(examples=[uuid.uuid4()])
