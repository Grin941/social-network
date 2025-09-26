import datetime
import typing

from cryptography import fernet
from jose import JWTError, jwt

from social_network.domain import exceptions as domain_exceptions
from social_network.domain import models
from social_network.domain.services import abstract
from social_network.infrastructure.database import exceptions as database_exceptions
from social_network.infrastructure.database import uow


class AuthService(abstract.AbstractService):
    def __init__(
        self,
        unit_of_work: uow.UnitOfWork,
        secret: str,
        algorithm: str,
        token_ttl_seconds: int,
    ) -> None:
        super().__init__(unit_of_work=unit_of_work)
        self._secret = secret
        self._algorithm = algorithm
        self._token_ttl_seconds = token_ttl_seconds

    def encrypt_password(self, password: str) -> str:
        try:
            return fernet.Fernet(self._secret).encrypt(password.encode()).decode()
        except ValueError as exc:
            raise domain_exceptions.FernetKeyError() from exc

    def decrypt_password(self, password: str) -> str:
        try:
            return fernet.Fernet(self._secret).decrypt(password).decode()
        except ValueError as exc:
            raise domain_exceptions.FernetKeyError() from exc
        except (fernet.InvalidToken, fernet.InvalidSignature) as exc:
            raise domain_exceptions.FernetInvalidTokenError(str(exc)) from exc

    def create_access_token(self, id_: str) -> str:
        return jwt.encode(
            {
                "sub": id_,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(seconds=self._token_ttl_seconds),
            },
            key=self._secret,
            algorithm=self._algorithm,
        )

    def decode_access_token(self, token: str) -> dict[str, typing.Any]:
        try:
            return jwt.decode(
                token=token, key=self._secret, algorithms=[self._algorithm]
            )
        except JWTError:
            raise domain_exceptions.InvalidTokenError(token)

    async def _duplicate_exists(self, item: models.NewUserDomain) -> bool:
        async for _ in self._uow.transaction(read_only=True):
            users = await self._uow.users.find_all(
                item.model_dump(exclude={"password"})
            )
        for user in users:
            if self.decrypt_password(password=user.password) == item.password:
                return True

        return False

    async def register(self, new_user: models.NewUserDomain) -> models.UserDomain:
        if await self._duplicate_exists(new_user):
            raise domain_exceptions.UserAlreadyRegisteredError()

        async for _ in self._uow.transaction():
            user = await self._uow.users.create(
                models.NewUserDomain(
                    **new_user.model_dump(exclude={"password"}),
                    password=self.encrypt_password(password=new_user.password),
                )
            )
        return user

    async def authorize(self, token: str) -> models.UserDomain:
        payload = self.decode_access_token(token)
        expire = payload.get("exp", 0)
        expire_time = datetime.datetime.fromtimestamp(
            int(expire), tz=datetime.timezone.utc
        )
        if not expire or expire_time < datetime.datetime.now(datetime.timezone.utc):
            raise domain_exceptions.TokenIsExpired(token=token)

        if (user_id := payload.get("sub")) is None:
            raise domain_exceptions.InvalidTokenError(token)

        async for _ in self._uow.transaction(read_only=True):
            try:
                user = await self._uow.users.find_one(user_id)
            except database_exceptions.ObjectDoesNotExistError as exc:
                raise domain_exceptions.UserNotFoundError(user_id) from exc

        return user

    async def login(self, id_: str, password: str) -> str:
        async for _ in self._uow.transaction(read_only=True):
            try:
                user = await self._uow.users.find_one(id_)
            except database_exceptions.ObjectDoesNotExistError as err:
                raise domain_exceptions.UserNotFoundError(id_) from err

        if self.decrypt_password(password=user.password) != password:
            raise domain_exceptions.WrongPasswordError()

        return self.create_access_token(id_)
