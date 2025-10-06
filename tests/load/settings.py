import logging
import typing

import pydantic
import pydantic_settings

from data_generator import const as generator_const
from social_network.settings import AuthSettings, DbSettings, ServerSettings
from tests.load import const as test_const

logger = logging.getLogger(__name__)


class TimescaleSettings(pydantic_settings.BaseSettings):
    host: str = "localhost"
    port: int = pydantic.Field(default=5432, alias="TIMESCALE_PORT")
    user: str = pydantic.Field(default="timescale", alias="TIMESCALE_USER")
    password: str = pydantic.Field(default="", alias="TIMESCALE_PASSWORD")
    database: str = pydantic.Field(default="timescale", alias="TIMESCALE_DATABASE")

    def print_to_log(self) -> None:
        logger.info(f"timescale.host={self.host}")
        logger.info(f"timescale.port={self.port}")
        logger.info(f"timescale.user={self.user}")
        logger.info(f"timescale.password={self.password}")
        logger.info(f"timescale.database={self.database}")


class DataGeneratorSettings(pydantic_settings.BaseSettings):
    bio_sentences_count: int = generator_const.BIO_SENTENCES_COUNT
    entities_count: int = test_const.ENTITIES_COUNT
    batch_count: int = test_const.BATCH_COUNT
    name_split_count: int = test_const.SEARCH_SPLIT_COUNT
    search_ratio: int = 10
    get_ratio: int = 10
    registration_ratio: int = 10
    feed_ratio: int = 1000
    add_friend_ratio: int = 10
    delete_friend_ratio: int = 10
    write_post_ratio: int = 100
    update_post_ratio: int = 10
    delete_post_ratio: int = 10
    write_message_ratio: int = 1
    read_dialog_ratio: int = 2

    def print_to_log(self) -> None:
        logger.info(f"generator.bio_sentences_count={self.bio_sentences_count}")
        logger.info(f"generator.entities_count={self.entities_count}")
        logger.info(f"generator.batch_count={self.batch_count}")
        logger.info(f"generator.name_split_count={self.name_split_count}")
        logger.info(f"generator.search_ratio={self.search_ratio}")
        logger.info(f"generator.get_ratio={self.get_ratio}")
        logger.info(f"generator.registration_ratio={self.registration_ratio}")
        logger.info(f"generator.feed_ratio={self.feed_ratio}")
        logger.info(f"generator.add_friend_ratio={self.add_friend_ratio}")
        logger.info(f"generator.delete_friend_ratio={self.delete_friend_ratio}")
        logger.info(f"generator.write_post_ratio={self.write_post_ratio}")
        logger.info(f"generator.update_post_ratio={self.update_post_ratio}")
        logger.info(f"generator.delete_post_ratio={self.delete_post_ratio}")
        logger.info(f"generator.write_message_ratio={self.write_message_ratio}")
        logger.info(f"generator.read_dialog_ratio={self.read_dialog_ratio}")


class LoadTestsSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    server: ServerSettings = pydantic.Field(default_factory=ServerSettings)
    timescale: TimescaleSettings = pydantic.Field(default_factory=TimescaleSettings)
    db: DbSettings = pydantic.Field(default_factory=DbSettings)
    auth: AuthSettings = pydantic.Field(default_factory=AuthSettings)
    data_generator: DataGeneratorSettings = pydantic.Field(
        default_factory=DataGeneratorSettings
    )

    log_level: str = "DEBUG"
    locale: str = generator_const.LOCALE
    seed: int = generator_const.SEED

    @property
    def logging(self) -> dict[str, typing.Any]:
        return {
            "version": 1,
            "formatters": {
                "aardvark": {
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)15s.%(msecs)03d %(processName)s"
                    " pid:%(process)d tid:%(thread)d %(levelname)s"
                    " %(name)s:%(lineno)d %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "aardvark",
                    "stream": "ext://sys.stderr",
                },
            },
            "root": {"level": self.log_level, "handlers": ["console"]},
        }

    def print_to_log(self) -> None:
        self.server.print_to_log()
        self.timescale.print_to_log()
        self.db.print_to_log()
        self.auth.print_to_log()
        self.data_generator.print_to_log()
        logger.info(f"settings.level={self.log_level}")
        logger.info(f"settings.locale={self.locale}")
        logger.info(f"settings.seed={self.seed}")
