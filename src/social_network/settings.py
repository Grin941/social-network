import logging

import pydantic
import pydantic_settings


class ServerSettings(pydantic.BaseModel):
    bind_host: str = "0.0.0.0"
    bind_port: int = 8080
    workers: int = pydantic.Field(default=1, gt=0)

    def print_to_log(self, log: logging.Logger) -> None:
        log.info(f"server.bind_host={self.bind_port}")
        log.info(f"server.bind_port={self.bind_port}")
        log.info(f"server.workers={self.workers}")


class DbSettings(pydantic.BaseModel):
    typename: str = "postgresql+psycopg2"
    username: str = "socnet"
    password: str = ""
    host: str = "127.0.0.1"
    port: int = 5432
    name: str = "socialnetwork"
    pool_size: int = pydantic.Field(default=1, gt=0)

    @property
    def connection_url(self) -> str:
        return f"{self.typename}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

    def print_to_log(self, log: logging.Logger) -> None:
        log.info(f"db.typename={self.typename}")
        log.info(f"db.username={self.username}")
        log.info(f"db.host={self.host}")
        log.info(f"db.port={self.port}")
        log.info(f"db.name={self.name}")
        log.info(f"db.pool_size={self.pool_size}")


class AuthSettings(pydantic.BaseModel):
    secret: str = ""
    algorithm: str = "HS256"

    def print_to_log(self, log: logging.Logger) -> None:
        log.info(f"auth.algorithm={self.algorithm}")


class SocialNetworkSettings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    server: ServerSettings = pydantic.Field(default_factory=ServerSettings)
    db: DbSettings = pydantic.Field(default_factory=DbSettings)
    auth: AuthSettings = pydantic.Field(default_factory=AuthSettings)

    level: str = "DEBUG"

    def print_to_log(self, log: logging.Logger) -> None:
        self.server.print_to_log(log)
        self.db.print_to_log(log)
        self.auth.print_to_log(log)
        log.info(f"settings.level={self.level}")
