import typing

import fastapi

from social_network.api.dependencies import services
from social_network.infrastructure import ws


async def get_feed_ws_manager(
    async_feed_service: services.AsyncFeedService,
) -> ws.WSConnectionManager:
    return ws.WSConnectionManager(async_service=async_feed_service)


WsManager = typing.Annotated[
    ws.WSConnectionManager, fastapi.Depends(get_feed_ws_manager)
]
