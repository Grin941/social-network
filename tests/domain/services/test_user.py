import pytest

from social_network.domain import exceptions, services, models


@pytest.mark.asyncio
async def test_get_user_that_not_exist(
    user_service_user_not_exists: services.UserService,
    user_id: str,
) -> None:
    with pytest.raises(exceptions.UserNotFoundError):
        assert await user_service_user_not_exists.get_user(user_id)


@pytest.mark.asyncio
async def test_get_user_that_exists(
    user_service_user_exists: services.UserService,
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> None:
    assert await user_service_user_exists.get_user(
        user_auth_data["id"]
    ) == models.UserDomain(**(new_user.model_dump() | user_auth_data))
