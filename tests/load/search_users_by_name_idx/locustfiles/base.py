import json
import logging
from logging import config as logging_config

import locust
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from data_generator import DataGenerator
from social_network.api import schema_mappers
from social_network.infrastructure.database import repository, uow
from tests.load import mixin, settings, shape

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


class BaseSearchShape(shape.DynamicUserShape):
    stages = [
        shape.Stage(
            users=1,
            spawn_rate=1,
            duration=30,
        ),
        shape.Stage(
            users=10,
            spawn_rate=1,
            duration=30,
        ),
        shape.Stage(
            users=100,
            spawn_rate=10,
            duration=60,
        ),
        shape.Stage(
            users=1000,
            spawn_rate=50,
            duration=60,
        ),
    ]


class BaseSetupTeardown(mixin.AsyncMixin):
    def __init__(self) -> None:
        super().__init__()

        self._settings = load_tests_settings
        self._logger = logger

        self._uow = uow.UnitOfWork(
            master_factory=async_sessionmaker(
                create_async_engine(
                    url=load_tests_settings.db.connection_url,
                    echo=load_tests_settings.log_level == "DEBUG",
                    pool_size=load_tests_settings.db.pool_size,
                ),
                expire_on_commit=False,
            ),
            user_repository=repository.UserRepository(),
        )

        self._generator = DataGenerator(
            seed=load_tests_settings.seed,
            locale=load_tests_settings.locale,
        )

    async def _create_users(self):
        self._logger.info("Creating users")
        async for transaction in self._uow.transaction():
            cursor = await transaction.execute_raw_query("SELECT COUNT(*) FROM users")
            (count,) = cursor.fetchone()

        entities_count = self._settings.user_generator.entities_count - count

        if entities_count <= 0:
            return

        batch = []
        for user in self._generator.generate_users(
            entities_count=entities_count,
            bio_sentences_count=self._settings.user_generator.bio_sentences_count,
        ):
            batch.append(user)
            if len(batch) == self._settings.user_generator.batch_count:
                async for _ in self._uow.transaction():
                    await self._uow.users.batch_create(batch)
                self._logger.debug(
                    f"Created {len(batch)} users. {entities_count} remaining"
                )
                batch = []

        if batch:
            async for _ in self._uow.transaction():
                await self._uow.users.batch_create(batch)

    def setup(self) -> None:
        self._run_async(self._create_users())

    def teardown(self) -> None:
        raise NotImplementedError()


class BaseSearchUser(locust.HttpUser):
    """
    Проверяем влияние индексов на
    - поиск
    - вставку

    При этом выставляем отношение read:write = 10:1
    """

    host: str | None = f"http://{load_tests_settings.server.bind}"
    abstract: bool = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._settings = load_tests_settings
        self._logger = logger

        self._generator = DataGenerator(
            seed=load_tests_settings.seed,
            locale=load_tests_settings.locale,
        )

    @locust.task(load_tests_settings.user_generator.search_ratio)
    def search(self) -> None:
        first_name_splitted = self._generator.generate_name()[
            : self._settings.user_generator.name_split_count
        ]
        last_name_splitted = self._generator.generate_last_name()[
            : self._settings.user_generator.name_split_count
        ]
        self._logger.debug(f"Searching for {first_name_splitted} {last_name_splitted}")
        response = self.client.get(
            f"/user/search?first_name={first_name_splitted}&last_name={last_name_splitted}",
            name="/search",
        )
        self._logger.debug(f"Found: {response.json()}")

    @locust.task(load_tests_settings.user_generator.registration_ratio)
    def register(self) -> None:
        new_user = self._generator.generate_user(
            bio_sentences_count=self._settings.user_generator.bio_sentences_count
        )
        response = self.client.post(
            "/user/register",
            json=json.loads(
                schema_mappers.RegistrationMapper.map_domain_to_dto(
                    new_user
                ).model_dump_json()
            ),
            name="/register",
        )
        self._logger.debug(f"Registered: {response.json()}")
