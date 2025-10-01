import datetime
import typing
import uuid
from unittest import mock

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
    user_unit_of_work: uow.UserUnitOfWork,
    algorithm: str,
    secret: str,
    token_ttl_seconds: int,
) -> services.AuthService:
    return services.AuthService(
        unit_of_work=user_unit_of_work,
        algorithm=algorithm,
        secret=secret,
        token_ttl_seconds=token_ttl_seconds,
    )


@pytest.fixture
def another_auth_service(
    user_unit_of_work: uow.UserUnitOfWork, algorithm: str, token_ttl_seconds: int
) -> services.AuthService:
    return services.AuthService(
        unit_of_work=user_unit_of_work,
        algorithm=algorithm,
        secret=fernet.Fernet.generate_key().decode(),
        token_ttl_seconds=token_ttl_seconds,
    )


@pytest.fixture
def auth_service_with_invalid_secret(
    user_unit_of_work: uow.UserUnitOfWork, algorithm: str, token_ttl_seconds: int
) -> services.AuthService:
    return services.AuthService(
        unit_of_work=user_unit_of_work,
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
    async def users_find_all(
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.UserDomain]:
        return [models.UserDomain(**(new_user.model_dump() | user_auth_data))]

    mocker.patch.object(auth_service.uow.users, "find_all", new=users_find_all)

    return auth_service


@pytest.fixture
def auth_service_without_duplicates(
    mocker: pytest_mock.MockerFixture,
    auth_service: services.AuthService,
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> services.AuthService:
    async def users_find_all(
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.UserDomain]:
        return []

    async def create_user(item: models.NewUserDomain) -> models.UserDomain:
        return models.UserDomain(**(new_user.model_dump() | user_auth_data))

    mocker.patch.object(auth_service.uow.users, "find_all", new=users_find_all)
    mocker.patch.object(auth_service.uow.users, "create", new=create_user)

    return auth_service


@pytest.fixture
def auth_service_user_not_exists(
    mocker: pytest_mock.MockerFixture,
    auth_service: services.AuthService,
) -> services.AuthService:
    async def find_user(id_: str) -> models.UserDomain:
        raise database_exceptions.ObjectDoesNotExistError(model="users", id_=id_)

    mocker.patch.object(auth_service.uow.users, "find_one", new=find_user)

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

    mocker.patch.object(auth_service.uow.users, "find_one", new=find_user)

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

    mocker.patch.object(auth_service.uow.users, "find_one", new=find_user)

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
    user_unit_of_work: uow.UserUnitOfWork,
) -> services.UserService:
    return services.UserService(unit_of_work=user_unit_of_work)


@pytest.fixture
def user_service_user_not_exists(
    mocker: pytest_mock.MockerFixture,
    user_service: services.UserService,
) -> services.UserService:
    async def find_user(id_: str) -> models.UserDomain:
        raise database_exceptions.ObjectDoesNotExistError(model="users", id_=id_)

    mocker.patch.object(user_service.uow.users, "find_one", new=find_user)

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

    mocker.patch.object(user_service.uow.users, "find_one", new=find_user)

    return user_service


@pytest.fixture
def post_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def post_author_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def new_post(post_author_id: uuid.UUID) -> models.NewPostDomain:
    return models.NewPostDomain(
        author_id=post_author_id,
        text="",
    )


@pytest.fixture
def updating_post(post_id: uuid.UUID) -> models.UpdatingPostDomain:
    return models.UpdatingPostDomain(
        id=post_id,
        text="new_text",
    )


@pytest.fixture
def existing_post(
    updating_post: models.UpdatingPostDomain, post_author_id: uuid.UUID
) -> models.PostDomain:
    return models.PostDomain(
        **(updating_post.model_dump() | {"author_id": post_author_id, "text": "text"})
    )


@pytest.fixture
def post_service(
    post_unit_of_work: uow.PostUnitOfWork,
    mocker: pytest_mock.MockerFixture,
    existing_post: models.PostDomain,
) -> services.PostService:
    post_service = services.PostService(unit_of_work=post_unit_of_work)

    async def create(item: models.NewPostDomain) -> models.PostDomain:
        return existing_post

    async def find_one(id_: str) -> models.PostDomain:
        return existing_post

    async def update(item: models.UpdatingPostDomain) -> models.PostDomain:
        item.updated_at = datetime.datetime.now(datetime.timezone.utc)
        return models.PostDomain(
            author_id=existing_post.author_id,
            **item.model_dump(),
        )

    async def delete(item: models.PostDomain) -> None:
        return None

    async def feed(
        user_id: uuid.UUID, offset: int, limit: int
    ) -> list[models.PostDomain]:
        return []

    mocker.patch.object(post_service.uow.posts, "create", new=create)
    mocker.patch.object(post_service.uow.posts, "find_one", new=find_one)
    mocker.patch.object(post_service.uow.posts, "update", new=update)
    mocker.patch.object(post_service.uow.posts, "delete", new=delete)
    mocker.patch.object(post_service.uow.posts, "delete", new=delete)
    mocker.patch.object(post_service.uow.posts, "feed", new=feed)

    return post_service


@pytest.fixture
def post_service_with_author_not_exists(
    post_service: services.PostService,
    mocker: pytest_mock.MockerFixture,
) -> services.PostService:
    async def create(item: models.NewPostDomain) -> models.PostDomain:
        raise database_exceptions.RelatedObjectDoesNotExistError(
            model="posts", fk_model="user", fk_value=str(uuid.uuid4())
        )

    mocker.patch.object(post_service.uow.posts, "create", new=create)

    return post_service


@pytest.fixture
def post_service_with_not_existing_post(
    post_service: services.PostService,
    mocker: pytest_mock.MockerFixture,
    post_id: uuid.UUID,
) -> services.PostService:
    async def find_one(id_: str) -> models.PostDomain:
        raise database_exceptions.ObjectDoesNotExistError(
            model="posts", id_=str(post_id)
        )

    mocker.patch.object(post_service.uow.posts, "find_one", new=find_one)

    return post_service


@pytest.fixture
def user(
    new_user: models.NewUserDomain,
    user_auth_data: dict[str, str],
) -> models.UserDomain:
    return models.UserDomain(**(new_user.model_dump() | user_auth_data))


@pytest.fixture
def friend_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def user_friend(
    user_id: uuid.UUID,
    friend_id: uuid.UUID,
) -> models.FriendDomain:
    return models.FriendDomain(
        id=uuid.uuid4(),
        user_id=user_id,
        friend_id=friend_id,
    )


@pytest.fixture
def reversed_friend(
    user_friend: models.FriendDomain,
) -> models.FriendDomain:
    return models.FriendDomain(
        id=uuid.uuid4(),
        user_id=user_friend.friend_id,
        friend_id=user_friend.user_id,
    )


@pytest.fixture
def patch_delete_friendship(
    mocker: pytest_mock.MockerFixture, friend_service: services.FriendService
) -> mock.MagicMock:
    async def delete(item: models.FriendDomain) -> None:
        return None

    return mocker.patch.object(friend_service.uow.friends, "delete", side_effect=delete)


@pytest.fixture
def friend_service(
    friend_unit_of_work: uow.FriendUnitOfWork,
    mocker: pytest_mock.MockerFixture,
    user_friend: models.FriendDomain,
    reversed_friend: models.FriendDomain,
) -> services.FriendService:
    async def create(item: models.NewFriendDomain) -> models.FriendDomain:
        return user_friend

    async def find_all(
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.FriendDomain]:
        if (filters or {}).get("user_id") == user_friend.user_id:
            return [user_friend]
        elif (filters or {}).get("user_id") == user_friend.friend_id:
            return [reversed_friend]
        else:
            return []

    service = services.FriendService(unit_of_work=friend_unit_of_work)

    mocker.patch.object(service.uow.friends, "create", new=create)
    mocker.patch.object(service.uow.friends, "find_all", new=find_all)

    return service


@pytest.fixture
def friend_service_with_not_existing_user(
    friend_service: services.FriendService,
    mocker: pytest_mock.MockerFixture,
    user_id: uuid.UUID,
    friend_id: uuid.UUID,
) -> services.FriendService:
    async def create(item: models.NewFriendDomain) -> models.FriendDomain:
        raise database_exceptions.RelatedObjectDoesNotExistError(
            model="friends", fk_model="users", fk_value=str(user_id)
        )

    async def find_all(
        exclude_deleted: bool = False,
        filters: typing.Optional[dict[str, typing.Any]] = None,
        order_by: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
    ) -> list[models.FriendDomain]:
        return []

    mocker.patch.object(friend_service.uow.friends, "create", new=create)
    mocker.patch.object(friend_service.uow.friends, "find_all", new=find_all)

    return friend_service
