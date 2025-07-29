import asyncio
import datetime

import pytest

from social_network.domain import exceptions, models, services


def test_password_encryption_with_invalid_secret(
    auth_service_with_invalid_secret: services.AuthService,
    password: str,
    secret: str,
) -> None:
    with pytest.raises(exceptions.FernetKeyError):
        assert auth_service_with_invalid_secret.decrypt_password(
            password=auth_service_with_invalid_secret.encrypt_password(
                password=password,
            )
        )


def test_password_encryption_differs_for_one_secret(
    auth_service: services.AuthService,
    password: str,
) -> None:
    assert auth_service.encrypt_password(
        password=password,
    ) != auth_service.encrypt_password(
        password=password,
    )


def test_password_decryption(
    auth_service: services.AuthService,
    password: str,
    secret: str,
) -> None:
    encrypted_password_1 = auth_service.encrypt_password(
        password=password,
    )
    encrypted_password_2 = auth_service.encrypt_password(
        password=password,
    )

    assert (
        auth_service.decrypt_password(
            password=encrypted_password_1,
        )
        == auth_service.decrypt_password(
            password=encrypted_password_2,
        )
        == password
    )


def test_password_decryption_with_invalid_secret(
    auth_service_with_invalid_secret: services.AuthService,
    password: str,
    secret: str,
) -> None:
    with pytest.raises(exceptions.FernetKeyError):
        assert auth_service_with_invalid_secret.decrypt_password(
            password=auth_service_with_invalid_secret.encrypt_password(
                password=password,
            ),
        )


def test_wrong_signature_password_decryption(
    auth_service: services.AuthService,
    another_auth_service: services.AuthService,
    password: str,
    secret: str,
) -> None:
    with pytest.raises(exceptions.FernetInvalidTokenError):
        assert auth_service.decrypt_password(
            password=another_auth_service.encrypt_password(
                password=password,
            ),
        )


@pytest.mark.asyncio
async def test_registration_if_duplicate_exists(
    auth_service_with_duplicates: services.AuthService,
    new_user: models.NewUserDomain,
) -> None:
    with pytest.raises(exceptions.UserAlreadyRegisteredError):
        assert await auth_service_with_duplicates.register(new_user)


@pytest.mark.asyncio
async def test_registration_if_no_duplicate_exists(
    auth_service_without_duplicates: services.AuthService,
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> None:
    assert await auth_service_without_duplicates.register(
        new_user
    ) == models.UserDomain(**(new_user.model_dump() | user_auth_data))


@pytest.mark.asyncio
async def test_login_user_not_exists(
    auth_service_user_not_exists: services.AuthService,
    user_auth_data: dict[str, str],
) -> None:
    with pytest.raises(exceptions.UserNotFoundError):
        assert await auth_service_user_not_exists.login(
            id_=user_auth_data["id"],
            password=user_auth_data["password"],
        )


@pytest.mark.asyncio
async def test_login_user_with_wrong_password(
    auth_service_user_with_wrong_password: services.AuthService,
    user_auth_data: dict[str, str],
) -> None:
    with pytest.raises(exceptions.WrongPasswordError):
        assert await auth_service_user_with_wrong_password.login(
            id_=user_auth_data["id"],
            password=user_auth_data["password"],
        )


@pytest.mark.asyncio
async def test_login(
    auth_service_user_exists: services.AuthService,
    user_auth_data: dict[str, str],
) -> None:
    token = await auth_service_user_exists.login(
        id_=user_auth_data["id"],
        password=auth_service_user_exists.decrypt_password(user_auth_data["password"]),
    )
    token_data = auth_service_user_exists.decode_access_token(token)
    assert datetime.datetime.fromtimestamp(
        int(token_data["exp"]), tz=datetime.timezone.utc
    ) >= datetime.datetime.now(datetime.timezone.utc)
    assert token_data["sub"] == user_auth_data["id"]


@pytest.mark.asyncio
async def test_invalid_token_authorization(
    auth_service: services.AuthService,
    invalid_token: str,
) -> None:
    with pytest.raises(exceptions.InvalidTokenError):
        assert await auth_service.authorize("invalid token")

    with pytest.raises(exceptions.InvalidTokenError):
        assert await auth_service.authorize(invalid_token)


@pytest.mark.asyncio
async def test_authorization_token_expired(
    auth_service_user_exists: services.AuthService,
    user_auth_data: dict[str, str],
    token_ttl_seconds: int,
) -> None:
    token = await auth_service_user_exists.login(
        id_=user_auth_data["id"],
        password=auth_service_user_exists.decrypt_password(user_auth_data["password"]),
    )
    await asyncio.sleep(token_ttl_seconds)

    with pytest.raises(exceptions.TokenIsExpired):
        assert await auth_service_user_exists.authorize(token)


@pytest.mark.asyncio
async def test_authorization_user_not_exist(
    auth_service_user_not_exists: services.AuthService,
    user_id: str,
) -> None:
    with pytest.raises(exceptions.UserNotFoundError):
        assert await auth_service_user_not_exists.authorize(
            auth_service_user_not_exists.create_access_token(user_id)
        )


@pytest.mark.asyncio
async def test_auth(
    auth_service_user_exists: services.AuthService,
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> None:
    assert await auth_service_user_exists.authorize(
        auth_service_user_exists.create_access_token(user_auth_data["id"])
    ) == models.UserDomain(**(new_user.model_dump() | user_auth_data))
