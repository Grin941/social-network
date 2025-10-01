import uuid

import pytest

from social_network.domain import exceptions, models, services


@pytest.mark.asyncio
async def test_make_post_author_not_found(
    post_service_with_author_not_exists: services.PostService,
    new_post: models.NewPostDomain,
) -> None:
    with pytest.raises(exceptions.AuthorNotFoundError):
        assert await post_service_with_author_not_exists.make_post(new_post)


@pytest.mark.asyncio
async def test_make_post(
    post_service: services.PostService,
    new_post: models.NewPostDomain,
    existing_post: models.PostDomain,
) -> None:
    post = await post_service.make_post(new_post)
    assert post == existing_post


@pytest.mark.asyncio
async def test_update_post_that_not_exists(
    post_service_with_not_existing_post: services.PostService,
    updating_post: models.UpdatingPostDomain,
    existing_post: models.PostDomain,
) -> None:
    with pytest.raises(exceptions.PostNotFoundError):
        assert await post_service_with_not_existing_post.update_post(
            post=updating_post, user_id=existing_post.author_id
        )


@pytest.mark.asyncio
async def test_update_post_if_user_is_not_author(
    post_service: services.PostService,
    updating_post: models.UpdatingPostDomain,
) -> None:
    with pytest.raises(exceptions.OnlyAuthorMayUpdatePostError):
        assert await post_service.update_post(post=updating_post, user_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_update_post(
    post_service: services.PostService,
    updating_post: models.UpdatingPostDomain,
    existing_post: models.PostDomain,
) -> None:
    post = await post_service.update_post(
        post=updating_post, user_id=existing_post.author_id
    )
    assert post.text == updating_post.text != existing_post.text


@pytest.mark.asyncio
async def test_delete_post_that_not_exists(
    post_service_with_not_existing_post: services.PostService,
    existing_post: models.PostDomain,
) -> None:
    with pytest.raises(exceptions.PostNotFoundError):
        assert await post_service_with_not_existing_post.delete_post(  # type: ignore[func-returns-value]
            post_id=existing_post.id, user_id=existing_post.author_id
        )


@pytest.mark.asyncio
async def test_delete_post_if_user_is_not_author(
    post_service: services.PostService,
    existing_post: models.PostDomain,
) -> None:
    with pytest.raises(exceptions.OnlyAuthorMayUpdatePostError):
        assert await post_service.delete_post(  # type: ignore[func-returns-value]
            post_id=existing_post.id, user_id=uuid.uuid4()
        )


@pytest.mark.asyncio
async def test_delete_post(
    post_service: services.PostService,
    existing_post: models.PostDomain,
) -> None:
    await post_service.delete_post(
        post_id=existing_post.id, user_id=existing_post.author_id
    )


@pytest.mark.asyncio
async def test_get_post_that_not_exists(
    post_service_with_not_existing_post: services.PostService,
) -> None:
    with pytest.raises(exceptions.PostNotFoundError):
        assert await post_service_with_not_existing_post.get_post(post_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_get_post(
    post_service: services.PostService,
    existing_post: models.PostDomain,
) -> None:
    assert (await post_service.get_post(post_id=existing_post.id)) == existing_post


@pytest.mark.asyncio
async def test_feed_posts(
    post_service: services.PostService,
    existing_post: models.PostDomain,
) -> None:
    assert (
        await post_service.feed(user_id=existing_post.author_id, offset=0, limit=10)
    ) == []
