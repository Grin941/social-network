import json
import logging
from logging import config as logging_config

import locust
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from data_generator import DataGenerator
from social_network.api import models as dto
from social_network.domain import models
from social_network.domain.services import auth
from social_network.infrastructure.database import repository
from tests.load import mixin, settings
from tests.load.test_cache.locustfiles import uow

logger = logging.getLogger("locust")

load_tests_settings = settings.LoadTestsSettings()
load_tests_settings.print_to_log()
logging_config.dictConfig(load_tests_settings.logging)


class BaseQueueUser(mixin.AsyncMixin, locust.HttpUser):
    """
    Проверяем влияние очередей на ленту новостей
    При этом выставляем отношение feed:write_post = 10:1
    """

    host: str | None = f"http://{load_tests_settings.server.bind}"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._settings = load_tests_settings
        self._logger = logger

        self._uow = uow.UnitOfWork(
            database_name=load_tests_settings.db.name,
            post_repository=repository.PostRepository(),
            friend_repository=repository.FriendRepository(),
            user_repository=repository.UserRepository(),
            master_factory=async_sessionmaker(
                create_async_engine(
                    url=load_tests_settings.db.connection_url,
                    echo=load_tests_settings.log_level == "DEBUG",
                    pool_size=load_tests_settings.db.pool_size,
                ),
                expire_on_commit=False,
            ),
        )

        self._generator = DataGenerator(
            seed=load_tests_settings.seed,
            locale=load_tests_settings.locale,
        )

    async def _get_random_user(self) -> tuple[models.UserDomain, str]:
        async for _ in self._uow.transaction():
            users = await self._uow.users.find_all(
                exclude_deleted=True,
                order_by="RANDOM()",
                limit=1,
            )
        user = users[0]
        return user, auth.create_access_token(
            id_=str(user.id),
            token_ttl_seconds=1_000_000,
            algorithm=self._settings.auth.algorithm,
            secret=self._settings.auth.secret,
        )

    @locust.task(load_tests_settings.data_generator.write_post_ratio)
    def write_post(self) -> None:
        user, token = self._run_async(self._get_random_user())
        post = self._generator.generate_post(user.id)
        self.client.post(
            "/post/create",
            json=json.loads(dto.NewPostDTO(**post.model_dump()).model_dump_json()),
            name="/create_post",
            headers={"Authorization": f"Bearer {token}"},
        )
