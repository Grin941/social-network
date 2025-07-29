import asyncio

loop = asyncio.get_event_loop()


class AsyncMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
