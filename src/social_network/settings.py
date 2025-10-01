import logging
import typing

import pydantic
import pydantic_settings

logger = logging.getLogger(__name__)


class ServerSettings(pydantic.BaseModel):
    bind_host: str = "0.0.0.0"
    bind_port: int = 8080
    workers: int = pydantic.Field(default=1, gt=0)

    @property
    def bind(self) -> str:
        return f"{self.bind_host}:{self.bind_port}"

    def print_to_log(self) -> None:
        logger.info(f"server.bind_host={self.bind_port}")
        logger.info(f"server.bind_port={self.bind_port}")
        logger.info(f"server.workers={self.workers}")


class DbSettings(pydantic.BaseModel):
    typename: str = "postgresql+asyncpg"
    username: str = "socnet"
    password: str = ""
    host: str = "127.0.0.1"
    port: int = 5432
    ro_port: typing.Optional[int] = None
    name: str = "socialnetwork"
    pool_size: int = pydantic.Field(default=1, gt=0)

    @property
    def connection_url(self) -> str:
        return f"{self.typename}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def ro_connection_url(self) -> typing.Optional[str]:
        if self.ro_port is None:
            return None
        return f"{self.typename}://{self.username}:{self.password}@{self.host}:{self.ro_port}/{self.name}"

    def print_to_log(self) -> None:
        logger.info(f"db.typename={self.typename}")
        logger.info(f"db.username={self.username}")
        logger.debug(f"db.password={self.password}")
        logger.info(f"db.host={self.host}")
        logger.info(f"db.port={self.port}")
        logger.info(f"db.ro_port={self.ro_port}")
        logger.info(f"db.name={self.name}")
        logger.info(f"db.pool_size={self.pool_size}")


class RedisSettings(pydantic.BaseModel):
    protocol: str = "redis"
    host: str = "127.0.0.1"
    port: int = 6379
    db: int = 0
    feed_capacity: int = 1000
    ttl: int = 600
    lock_timeout: float = 5.0

    @property
    def connection_url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}/{self.db}"

    def print_to_log(self) -> None:
        logger.info(f"redis.protocol={self.protocol}")
        logger.info(f"redis.host={self.host}")
        logger.debug(f"redis.port={self.port}")
        logger.info(f"redis.db={self.db}")
        logger.info(f"redis.feed_capacity={self.feed_capacity}")
        logger.info(f"redis.ttl={self.ttl}")
        logger.info(f"redis.lock_timeout={self.lock_timeout}")


class AuthSettings(pydantic.BaseModel):
    secret: str = ""
    algorithm: str = "HS256"
    token_ttl_seconds: int = 7 * 24 * 60 * 60

    def print_to_log(self) -> None:
        logger.debug(f"auth.secret={self.secret}")
        logger.info(f"auth.algorithm={self.algorithm}")
        logger.info(f"auth.token_ttl_seconds={self.token_ttl_seconds}")


class SentrySettings(pydantic.BaseModel):
    dsn: typing.Optional[str] = pydantic.Field(
        description="Sentry DSN host", default=None
    )
    environment: str = pydantic.Field(
        default="local", description="Environment name", examples=["prod", "dev"]
    )

    def print_to_log(
        self,
    ) -> None:
        logger.info(f"sentry.dsn={self.dsn}")
        logger.info(f"sentry.environment={self.environment}")


class SocialNetworkSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    server: ServerSettings = pydantic.Field(default_factory=ServerSettings)
    db: DbSettings = pydantic.Field(default_factory=DbSettings)
    redis: RedisSettings = pydantic.Field(default_factory=RedisSettings)
    auth: AuthSettings = pydantic.Field(default_factory=AuthSettings)
    sentry: SentrySettings = pydantic.Field(default_factory=SentrySettings)

    level: str = "INFO"

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
            "loggers": {
                "social_network": {"level": self.level, "handlers": ["console"]},
                "sqlalchemy": {"level": self.level, "handlers": ["console"]},
            },
            "root": {"level": self.level, "handlers": ["console"]},
        }

    def print_to_log(self) -> None:
        self.server.print_to_log()
        self.db.print_to_log()
        self.redis.print_to_log()
        self.auth.print_to_log()
        self.sentry.print_to_log()
        logger.info(f"settings.level={self.level}")
