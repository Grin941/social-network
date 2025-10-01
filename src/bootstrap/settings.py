import logging
import typing
import uuid

import pydantic
import pydantic_settings

from data_generator import const as generator_const
from social_network.settings import AuthSettings, DbSettings

logger = logging.getLogger(__name__)


class GeneratorSettings(pydantic_settings.BaseSettings):
    locale: str = generator_const.LOCALE
    seed: int = generator_const.SEED
    users_count: int = 10_000
    max_posts_per_user_count: int = 30
    max_user_friends_count: int = 100

    def print_to_log(self) -> None:
        logger.info(f"generator.locale={self.locale}")
        logger.info(f"generator.seed={self.seed}")
        logger.info(f"generator.users_count={self.users_count}")
        logger.info(
            f"generator.max_posts_per_user_count={self.max_posts_per_user_count}"
        )
        logger.info(f"generator.max_user_friends_count={self.max_user_friends_count}")


class BootstrapSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    my_password: str = ""
    my_uuid: uuid.UUID = uuid.uuid4()
    db: DbSettings = pydantic.Field(default_factory=DbSettings)
    auth: AuthSettings = pydantic.Field(default_factory=AuthSettings)
    generator: GeneratorSettings = pydantic.Field(default_factory=GeneratorSettings)

    log_level: str = "DEBUG"

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
        self.db.print_to_log()
        self.generator.print_to_log()
        self.auth.print_to_log()
        logger.info(f"settings.level={self.log_level}")
        logger.info(f"settings.my_password={self.my_password}")
        logger.info(f"settings.my_uuid={self.my_uuid}")
