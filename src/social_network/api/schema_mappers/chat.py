import uuid

from social_network.api import models as dto
from social_network.domain import models as domain


class MessageMapper:
    @staticmethod
    def map_domain_to_dto(
        message: domain.ChatMessageDomain, user_id: uuid.UUID, friend_id: uuid.UUID
    ) -> dto.MessageDTO:
        return dto.MessageDTO(
            **{  # type: ignore[arg-type]
                "from": message.author_id,
                "to": user_id if message.author_id == friend_id else friend_id,
                "text": message.text,
            }
        )
