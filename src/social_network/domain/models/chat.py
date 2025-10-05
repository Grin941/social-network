import typing
import uuid

import pydantic

from social_network.domain import mixins


class NewChatDomain(
    mixins.ModelWithCreatedAtUpdatedAtDeletedAtMixin, pydantic.BaseModel
):
    name: str
    owner_id: typing.Optional[uuid.UUID] = None


class ChatDomain(NewChatDomain):
    id: uuid.UUID


class NewChatParticipantDomain(
    mixins.ModelWithCreatedAtUpdatedAtDeletedAtMixin, pydantic.BaseModel
):
    user_id: uuid.UUID
    chat_id: uuid.UUID


class ChatParticipantDomain(NewChatParticipantDomain):
    id: uuid.UUID


class NewChatMessageDomain(
    mixins.ModelWithCreatedAtUpdatedAtDeletedAtMixin, pydantic.BaseModel
):
    author_id: uuid.UUID
    chat_id: uuid.UUID
    text: str


class ChatMessageDomain(NewChatMessageDomain):
    id: uuid.UUID
