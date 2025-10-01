import json
import logging
import random
import uuid
from logging import config as logging_config

import locust
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from data_generator import DataGenerator
from social_network.api import models as dto
from social_network.domain import models
from social_network.domain.services import auth
from social_network.infrastructure.database import repository
from tests.load import mixin, settings, shape
from tests.load.test_cache.locustfiles import uow

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
    Проверяем влияние кэша на ленту новостей
    При этом выставляем отношение feed:write_post:update_delete_post:update_friendship: = 100:10:1
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

    async def _get_random_friend(self, user_id: uuid.UUID) -> uuid.UUID:
        async for _ in self._uow.transaction():
            friends = await self._uow.friends.find_all(
                exclude_deleted=True,
                filters={"user_id": user_id},
                order_by="RANDOM()",
                limit=1,
            )
        return friends[0].friend_id

    async def _get_random_post(self, user_id: uuid.UUID) -> models.PostDomain:
        async for _ in self._uow.transaction():
            posts = await self._uow.posts.find_all(
                exclude_deleted=True,
                filters={"author_id": user_id},
                order_by="RANDOM()",
                limit=1,
            )
        return posts[0]

    @locust.task(load_tests_settings.data_generator.feed_ratio)
    def feed(self) -> None:
        _, token = self._run_async(self._get_random_user())
        logger.info(f"Feeding User: {_} Token: {token}")
        self.client.get(
            f"/post/feed?offset=0&limit={random.randrange(10, 1200)}",
            name="/feed",
            headers={"Authorization": f"Bearer {token}"},
        )

    @locust.task(load_tests_settings.data_generator.add_friend_ratio)
    def add_friend(self) -> None:
        _, token = self._run_async(self._get_random_user())
        user, _ = self._run_async(self._get_random_user())
        self.client.put(
            f"/friend/set/{user.id}",
            name="/set_friend",
            headers={"Authorization": f"Bearer {token}"},
        )

    @locust.task(load_tests_settings.data_generator.delete_friend_ratio)
    def delete_friend(self) -> None:
        user, token = self._run_async(self._get_random_user())
        self.client.put(
            f"/friend/delete/{self._run_async(self._get_random_friend(user))}",
            name="/delete_friend",
            headers={"Authorization": f"Bearer {token}"},
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

    @locust.task(load_tests_settings.data_generator.update_post_ratio)
    def update_post(self) -> None:
        user, token = self._run_async(self._get_random_user())
        post = self._run_async(self._get_random_post(user.id))
        post.text = self._generator.generate_text()
        self.client.put(
            "/post/update",
            json=json.loads(dto.UpdatingPostDTO(**post.model_dump()).model_dump_json()),
            name="/update_post",
            headers={"Authorization": f"Bearer {token}"},
        )

    @locust.task(load_tests_settings.data_generator.delete_post_ratio)
    def delete_post(self) -> None:
        user, token = self._run_async(self._get_random_user())
        post = self._run_async(self._get_random_post(user.id))
        post.text = self._generator.generate_text()
        self.client.put(
            f"/post/delete/{post.id}",
            name="/delete_post",
            headers={"Authorization": f"Bearer {token}"},
        )
