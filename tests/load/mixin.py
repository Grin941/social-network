import asyncio
import threading
import typing

# Global variables for the async event loop and thread
_async_loop = None
_async_thread = None
_loop_lock = threading.Lock()


class AsyncMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @staticmethod
    def _start_async_loop() -> None:
        """Starts the asyncio event loop in a new thread."""
        global _async_loop
        global _async_thread
        with _loop_lock:
            if _async_loop is None:
                _async_loop = asyncio.new_event_loop()
                _async_thread = threading.Thread(
                    target=_async_loop.run_forever, daemon=True
                )
                _async_thread.start()

    def _run_async(self, coro) -> typing.Any:
        """Runs an async coroutine from a synchronous function."""
        self._start_async_loop()
        future = asyncio.run_coroutine_threadsafe(
            coro, typing.cast(asyncio.AbstractEventLoop, _async_loop)
        )
        return future.result()
