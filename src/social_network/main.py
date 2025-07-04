import uvicorn

from social_network import settings
from social_network.api import app


def main() -> None:
    social_network_settings = settings.SocialNetworkSettings()
    uvicorn.run(
        app.build_application(),
        host=social_network_settings.server.bind_host,
        port=social_network_settings.server.bind_port,
    )


if __name__ == "__main__":
    main()
