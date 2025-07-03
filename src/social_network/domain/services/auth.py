import datetime
from jose import jwt, JWTError
from cryptography import fernet
import logging

from social_network.database import uow

from social_network.domain.services import abstract

from social_network.domain import models, exceptions as domain_exceptions
from social_network.database import exceptions as db_exceptions


class AuthService(abstract.AbstractService):
    def __init__(
        self,
        unit_of_work: uow.UnitOfWork,
        logger: logging.Logger,
        secret: str,
        algorithm: str,
    ) -> None:
        super().__init__(unit_of_work=unit_of_work, logger=logger)
        self._secret = secret
        self._algorithm = algorithm

    @staticmethod
    def _encrypt_password(password: str, secret: str) -> str:
        return fernet.Fernet(secret).encrypt(password.encode()).decode()

    @staticmethod
    def _decrypt_password(password: str, secret: str) -> str:
        return fernet.Fernet(secret).decrypt(password).decode()

    @staticmethod
    def create_access_token(id_: str, secret: str, algorithm: str) -> str:
        return jwt.encode(
            {
                "sub": id_,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(days=30),
            },
            key=secret,
            algorithm=algorithm,
        )

    async def register(self, new_user: models.NewUserDomain) -> models.UserDomain:
        async with self._uow.transaction():
            try:
                return await self._uow.users.create(
                    models.NewUserDomain(
                        **new_user.model_dump(),
                        password=self._encrypt_password(
                            password=new_user.password, secret=self._secret
                        ),
                    )
                )
            except db_exceptions.ObjectAlreadyExistsError as exc:
                raise domain_exceptions.UserAlreadyRegisteredError() from exc

    async def authorize(self, token: str) -> models.UserDomain:
        try:
            payload = jwt.decode(
                token=token, key=self._secret, algorithms=[self._algorithm]
            )
        except JWTError:
            raise domain_exceptions.InvalidTokenError(token)

        expire = payload.get("exp", 0)
        expire_time = datetime.datetime.fromtimestamp(
            int(expire), tz=datetime.timezone.utc
        )
        if not expire or expire_time < datetime.datetime.now(datetime.timezone.utc):
            raise domain_exceptions.TokenIsExpired(token=token)

        if (user_id := payload.get("sub")) is None:
            raise domain_exceptions.InvalidTokenError(token)

        async with self._uow.transaction():
            user = await self._uow.users.find_one(user_id)

        if not user:
            raise domain_exceptions.UserNotFoundError(user_id)

        return user

    async def login(self, id_: str, password: str) -> str:
        async with self._uow.transaction():
            user = await self._uow.users.find_one(id_)

        if not user:
            raise domain_exceptions.UserNotFoundError(id_)
        if user.password != self._encrypt_password(
            password=password, secret=self._secret
        ):
            raise domain_exceptions.WrongPasswordError()

        return self.create_access_token(
            id_=id_, secret=self._secret, algorithm=self._algorithm
        )
