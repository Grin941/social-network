import uuid

from social_network.api import models as dto
from social_network.domain import models as domain


class PostMapper:
    @staticmethod
    def map_new_dto_to_new_domain(
        new_post_dto: dto.NewPostDTO, author_id: uuid.UUID
    ) -> domain.NewPostDomain:
        return domain.NewPostDomain(author_id=author_id, **new_post_dto.model_dump())

    @staticmethod
    def map_domain_to_dto(post_domain: domain.PostDomain) -> dto.PostDTO:
        return dto.PostDTO(
            id=post_domain.id,
            text=post_domain.text,
            author_user_id=post_domain.author_id,
        )

    @staticmethod
    def map_updating_dto_to_updating_domain(
        updating_post_dto: dto.UpdatingPostDTO,
    ) -> domain.UpdatingPostDomain:
        return domain.UpdatingPostDomain(**updating_post_dto.model_dump())
