import uuid
from unittest import mock

import pytest

from social_network.domain import exceptions, models, services


@pytest.mark.asyncio
async def test_make_friendship_user_not_found(
    friend_service_with_not_existing_user: services.FriendService,
    user: models.UserDomain,
) -> None:
    with pytest.raises(exceptions.FriendNotFoundError):
        assert await friend_service_with_not_existing_user.make_friendship(
            user=user, friend_id=uuid.uuid4()
        )


@pytest.mark.asyncio
async def test_make_friend(
    friend_service: services.FriendService,
    user: models.UserDomain,
    user_friend: models.FriendDomain,
) -> None:
    friend = await friend_service.make_friendship(
        user=user, friend_id=user_friend.friend_id
    )
    assert friend == user_friend


@pytest.mark.asyncio
async def test_delete_friendship_user_not_found(
    friend_service_with_not_existing_user: services.FriendService,
    user: models.UserDomain,
) -> None:
    with pytest.raises(exceptions.FriendNotFoundError):
        assert await friend_service_with_not_existing_user.delete_friendship(  # type: ignore[func-returns-value]
            user=user, friend_id=uuid.uuid4()
        )


@pytest.mark.asyncio
async def test_delete_friendship(
    friend_service: services.FriendService,
    user: models.UserDomain,
    user_friend: models.FriendDomain,
    reversed_friend: models.FriendDomain,
    patch_delete_friendship: mock.MagicMock,
) -> None:
    await friend_service.delete_friendship(  # type: ignore[func-returns-value]
        user=user, friend_id=user_friend.friend_id
    )

    assert len(patch_delete_friendship.call_args_list) == 2
    assert patch_delete_friendship.call_args_list[0] == mock.call(user_friend)
    assert patch_delete_friendship.call_args_list[1] == mock.call(reversed_friend)
