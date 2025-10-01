import typing
import uuid

from social_network.domain import exceptions as domain_exceptions
from social_network.domain import models
from social_network.domain.services import abstract
from social_network.infrastructure.database import (
    exceptions as database_exceptions,
)
from social_network.infrastructure.database import (
    uow,
)


class PostService(abstract.AbstractService):
    @property
    def uow(self) -> uow.PostUnitOfWork:
        return typing.cast(uow.PostUnitOfWork, self._uow)

    async def make_post(self, post: models.NewPostDomain) -> models.PostDomain:
        async for _ in self.uow.transaction():
            try:
                new_post = await self.uow.posts.create(post)
            except database_exceptions.RelatedObjectDoesNotExistError as err:
                raise domain_exceptions.AuthorNotFoundError(
                    str(post.author_id)
                ) from err
        return new_post

    async def update_post(
        self, post: models.UpdatingPostDomain, user_id: uuid.UUID
    ) -> models.PostDomain:
        try:
            db_post = await self.get_post(post.id)
        except database_exceptions.ObjectDoesNotExistError as err:
            raise domain_exceptions.PostNotFoundError(str(post.id)) from err
        else:
            if db_post.author_id != user_id:
                raise domain_exceptions.OnlyAuthorMayUpdatePostError(
                    id_=str(post.id),
                    author_id=str(db_post.author_id),
                    user_id=str(user_id),
                )
            async for _ in self.uow.transaction():
                updating_post = await self.uow.posts.update(post)
        return updating_post

    async def delete_post(self, post_id: uuid.UUID, user_id: uuid.UUID) -> None:
        try:
            post = await self.get_post(post_id)
        except database_exceptions.ObjectDoesNotExistError as err:
            raise domain_exceptions.PostNotFoundError(str(post_id)) from err
        else:
            if post.author_id != user_id:
                raise domain_exceptions.OnlyAuthorMayUpdatePostError(
                    id_=str(post_id),
                    author_id=str(post.author_id),
                    user_id=str(user_id),
                )
            async for _ in self.uow.transaction():
                await self.uow.posts.delete(post)
        return None

    async def get_post(self, post_id: uuid.UUID) -> models.PostDomain:
        async for _ in self.uow.transaction():
            try:
                post = await self.uow.posts.find_one(str(post_id))
            except database_exceptions.ObjectDoesNotExistError as err:
                raise domain_exceptions.PostNotFoundError(str(post_id)) from err
        if post.deleted_at:
            raise domain_exceptions.PostNotFoundError(str(post_id))
        else:
            return post

    async def feed(
        self, user_id: uuid.UUID, offset: int, limit: int
    ) -> list[models.PostDomain]:
        async for _ in self.uow.transaction():
            posts = await self.uow.posts.feed(
                user_id=user_id, offset=offset, limit=limit
            )
        return posts
