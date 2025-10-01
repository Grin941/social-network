from social_network.infrastructure.database.repository.abstract import (
    AbstractRepository,
)
from social_network.infrastructure.database.repository.friend import (
    FriendRepository,
)
from social_network.infrastructure.database.repository.post import (
    PostRepository,
)
from social_network.infrastructure.database.repository.user import (
    UserRepository,
)

__all__ = [
    "AbstractRepository",
    "FriendRepository",
    "PostRepository",
    "UserRepository",
]
