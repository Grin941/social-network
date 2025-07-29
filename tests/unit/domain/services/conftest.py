import datetime
import typing
import uuid

import pytest
import pytest_mock
from cryptography import fernet
from jose import jwt

from social_network.domain import models, services
from social_network.infrastructure.database import exceptions as database_exceptions
from social_network.infrastructure.database import uow


@pytest.fixture
def algorithm() -> str:
    return "HS256"


@pytest.fixture
def secret() -> str:
    return fernet.Fernet.generate_key().decode()


@pytest.fixture
def password() -> str:
    return "passw0rd"


@pytest.fixture
def token_ttl_seconds() -> int:
    return 1


@pytest.fixture
def auth_service(
    unit_of_work: uow.UnitOfWork, algorithm: str, secret: str, token_ttl_seconds: int
) -> services.AuthService:
    return services.AuthService(
        unit_of_work=unit_of_work,
        algorithm=algorithm,
        secret=secret,
        token_ttl_seconds=token_ttl_seconds,
    )


@pytest.fixture
def another_auth_service(
    unit_of_work: uow.UnitOfWork, algorithm: str, token_ttl_seconds: int
) -> services.AuthService:
    return services.AuthService(
        unit_of_work=unit_of_work,
        algorithm=algorithm,
        secret=fernet.Fernet.generate_key().decode(),
        token_ttl_seconds=token_ttl_seconds,
    )


@pytest.fixture
def auth_service_with_invalid_secret(
    unit_of_work: uow.UnitOfWork, algorithm: str, token_ttl_seconds: int
) -> services.AuthService:
    return services.AuthService(
        unit_of_work=unit_of_work,
        algorithm=algorithm,
        secret="secret",
        token_ttl_seconds=token_ttl_seconds,
    )


@pytest.fixture
def new_user(password: str) -> models.NewUserDomain:
    return models.NewUserDomain(
        first_name="Ivan",
        second_name="Ivanov",
        birthdate=datetime.datetime.now(tz=datetime.timezone.utc),
        biography="Good guy",
        city="Moscow",
        password=password,
    )


@pytest.fixture
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def user_auth_data(
    password: str, auth_service: services.AuthService, user_id: str
) -> dict[str, str]:
    return {
        "password": auth_service.encrypt_password(password),
        "id": user_id,
    }


@pytest.fixture
def auth_service_with_duplicates(
    mocker: pytest_mock.MockerFixture,
    auth_service: services.AuthService,
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> services.AuthService:
    async def users_find_all(filters: dict[str, typing.Any]) -> list[models.UserDomain]:
        return [models.UserDomain(**(new_user.model_dump() | user_auth_data))]

    mocker.patch.object(auth_service._uow.users, "find_all", new=users_find_all)

    return auth_service


@pytest.fixture
def auth_service_without_duplicates(
    mocker: pytest_mock.MockerFixture,
    auth_service: services.AuthService,
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> services.AuthService:
    async def users_find_all(filters: dict[str, typing.Any]) -> list[models.UserDomain]:
        return []

    async def create_user(item: models.NewUserDomain) -> models.UserDomain:
        return models.UserDomain(**(new_user.model_dump() | user_auth_data))

    mocker.patch.object(auth_service._uow.users, "find_all", new=users_find_all)
    mocker.patch.object(auth_service._uow.users, "create", new=create_user)

    return auth_service


@pytest.fixture
def auth_service_user_not_exists(
    mocker: pytest_mock.MockerFixture,
    auth_service: services.AuthService,
) -> services.AuthService:
    async def find_user(id_: str) -> models.UserDomain:
        raise database_exceptions.ObjectDoesNotExistError(model="users", id_=id_)

    mocker.patch.object(auth_service._uow.users, "find_one", new=find_user)

    return auth_service


@pytest.fixture
def auth_service_user_with_wrong_password(
    mocker: pytest_mock.MockerFixture,
    auth_service: services.AuthService,
    new_user: models.NewUserDomain,
    user_id: str,
) -> services.AuthService:
    async def find_user(id_: str) -> models.UserDomain:
        return models.UserDomain(
            **(
                new_user.model_dump()
                | {
                    "id": user_id,
                    "password": auth_service.encrypt_password("<PASSWORD>"),
                }
            )
        )

    mocker.patch.object(auth_service._uow.users, "find_one", new=find_user)

    return auth_service


@pytest.fixture
def auth_service_user_exists(
    mocker: pytest_mock.MockerFixture,
    auth_service: services.AuthService,
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> services.AuthService:
    async def find_user(id_: str) -> models.UserDomain:
        return models.UserDomain(**(new_user.model_dump() | user_auth_data))

    mocker.patch.object(auth_service._uow.users, "find_one", new=find_user)

    return auth_service


@pytest.fixture
def invalid_token(secret: str, algorithm: str, token_ttl_seconds) -> str:
    return jwt.encode(
        {
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=token_ttl_seconds),
        },
        key=secret,
        algorithm=algorithm,
    )


@pytest.fixture
def user_service(
    unit_of_work: uow.UnitOfWork,
) -> services.UserService:
    return services.UserService(unit_of_work=unit_of_work)


@pytest.fixture
def user_service_user_not_exists(
    mocker: pytest_mock.MockerFixture,
    user_service: services.UserService,
) -> services.UserService:
    async def find_user(id_: str) -> models.UserDomain:
        raise database_exceptions.ObjectDoesNotExistError(model="users", id_=id_)

    mocker.patch.object(user_service._uow.users, "find_one", new=find_user)

    return user_service


@pytest.fixture
def user_service_user_exists(
    mocker: pytest_mock.MockerFixture,
    user_service: services.UserService,
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> services.UserService:
    async def find_user(id_: str) -> models.UserDomain:
        return models.UserDomain(**(new_user.model_dump() | user_auth_data))

    mocker.patch.object(user_service._uow.users, "find_one", new=find_user)

    return user_service
