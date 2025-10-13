import logging
from logging import config as logging_config

import locust
import websockets
from locust.contrib.socketio import SocketIOUser

from tests.load import settings, shape
from tests.load.test_queues.locustfiles.base import BaseQueueUser

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


class QueueUser(SocketIOUser, BaseQueueUser):
    async def _connect(self, token: str) -> None:
        async with websockets.connect(
            f"ws://{load_tests_settings.server.bind}/post/feed/posted?token={token}"
        ) as websocket:
            while True:
                await websocket.recv()

    def on_start(self) -> None:
        _, token = self._run_async(self._get_random_user())
        self._run_async(self._connect(token))
