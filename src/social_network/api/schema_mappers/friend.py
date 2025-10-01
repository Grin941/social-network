from social_network.api import models as dto
from social_network.domain import models as domain


class FriendMapper:
    @staticmethod
    def map_domain_to_dto(friendship: domain.FriendDomain) -> dto.FriendDTO:
        return dto.FriendDTO(
            user_id=friendship.user_id,
            friend_id=friendship.friend_id,
            created_at=friendship.created_at,
        )
