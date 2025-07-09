from logging import config as logging_config

import sentry_sdk
import uvicorn

from social_network import settings
from social_network.api import app


def main() -> None:
    social_network_settings = settings.SocialNetworkSettings()
    logging_config.dictConfig(social_network_settings.logging)
    social_network_settings.print_to_log()

    sentry_sdk.init(
        environment=social_network_settings.sentry.environment,
        dsn=social_network_settings.sentry.dsn,
    )

    uvicorn.run(
        app.build_application(),
        host=social_network_settings.server.bind_host,
        port=social_network_settings.server.bind_port,
    )


if __name__ == "__main__":
    main()
