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
from tests.load import mixin, settings, shape
from tests.load.test_sharding.locustfiles import uow

logger = logging.getLogger("locust")

load_tests_settings = settings.LoadTestsSettings()
load_tests_settings.print_to_log()
logging_config.dictConfig(load_tests_settings.logging)


@locust.events.init.add_listener
def on_locust_init(environment, **kwargs) -> None:
    environment.parsed_options.pghost = load_tests_settings.timescale.host
    environment.parsed_options.pgport = load_tests_settings.timescale.port
    environment.parsed_options.pguser = load_tests_settings.timescale.user
    environment.parsed_options.pgpassword = load_tests_settings.timescale.password
    environment.parsed_options.pgdatabase = load_tests_settings.timescale.database


class SearchShape(shape.DynamicUserShape):
    stages = [
        shape.Stage(
            users=1,
            spawn_rate=1,
            duration=60,
        ),
        shape.Stage(
            users=10,
            spawn_rate=1,
            duration=60,
        ),
        shape.Stage(
            users=100,
            spawn_rate=10,
            duration=90,
        ),
        shape.Stage(
            users=1000,
            spawn_rate=50,
            duration=90,
        ),
    ]


class CacheUser(mixin.AsyncMixin, locust.HttpUser):
    """
    Проверяем влияние шардирования на диалоги пользователей
    При этом выставляем отношение read:write = 2:1
    """

    host: str | None = f"http://{load_tests_settings.server.bind}"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._settings = load_tests_settings
        self._logger = logger

        self._uow = uow.UnitOfWork(
            database_name=load_tests_settings.db.name,
            friend_repository=repository.FriendRepository(),
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

    async def _get_random_friend(self) -> tuple[models.FriendDomain, str]:
        async for _ in self._uow.transaction():
            friends = await self._uow.friends.find_all(
                exclude_deleted=True,
                order_by="RANDOM()",
                limit=1,
            )
        friend = friends[0]
        return friend, auth.create_access_token(
            id_=str(friend.user_id),
            token_ttl_seconds=1_000_000,
            algorithm=self._settings.auth.algorithm,
            secret=self._settings.auth.secret,
        )

    @locust.task(load_tests_settings.data_generator.write_message_ratio)
    def write_message(self) -> None:
        friend, token = self._run_async(self._get_random_friend())
        logger.info(
            f"User: {friend.user_id} writes message to the friend {friend.friend_id} Token: {token}"
        )
        self.client.post(
            f"/dialog/{friend.friend_id}/send",
            name="/send_dialog_message",
            headers={"Authorization": f"Bearer {token}"},
            json=json.loads(
                dto.NewMessageDTO(
                    text=self._generator.generate_text(1)
                ).model_dump_json()
            ),
        )

    @locust.task(load_tests_settings.data_generator.read_dialog_ratio)
    def read_dialog(self) -> None:
        friend, token = self._run_async(self._get_random_friend())
        logger.info(
            f"User: {friend.user_id} reads dialog with the friend {friend.friend_id} Token: {token}"
        )
        self.client.get(
            f"/dialog/{friend.friend_id}/list",
            name="/list_dialog",
            headers={"Authorization": f"Bearer {token}"},
        )
