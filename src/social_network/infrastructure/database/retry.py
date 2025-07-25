import asyncio
import logging
import time
import types
import typing

DEFAULT_RETRIES_MAX_ATTEMPTS = 10
DEFAULT_RETRY_DELAY_SECONDS = 1

ExceptionHandlers = dict[
    typing.Type[BaseException], typing.Optional[typing.Callable[[BaseException], bool]]
]


class RetryAttempt:
    def __init__(
        self,
        notify_success: typing.Callable[..., None],
        max_attempts: int,
        exceptions_handlers: typing.Optional[ExceptionHandlers] = None,
    ) -> None:
        self._notify_success = notify_success
        self._attempt_number = 0
        self._max_attempts = max_attempts
        self._logger = logging.getLogger(__name__)
        self._exceptions_handlers = exceptions_handlers or {}

    def __enter__(self) -> None:
        self._attempt_number += 1

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> bool:
        if not exc_type:
            self._notify_success()
            return True

        if self._attempt_number <= self._max_attempts:
            for exception_type, handler in self._exceptions_handlers.items():
                if exc_type is exception_type or issubclass(exc_type, exception_type):
                    exception_is_handled = True
                    if handler:
                        exception_is_handled = handler(
                            typing.cast(BaseException, exc_val)
                        )

                    self._logger.debug(
                        f"Detected {exc_type} while attempt {self._attempt_number}."
                    )
                    return exception_is_handled

        return False


def retry(
    max_attempts: int = DEFAULT_RETRIES_MAX_ATTEMPTS,
    delay: float = DEFAULT_RETRY_DELAY_SECONDS,
    exceptions_handlers: typing.Optional[ExceptionHandlers] = None,
) -> typing.Generator[RetryAttempt, None, None]:
    """Retry a piece of code in case of certain exceptions

    Args:
        max_attempts (int): do retry this times
        delay (float): delay between attempts
        exceptions_handlers (Optional[ExceptionHandlers]): dict with exceptions and their handlers

    Yields:
        RetryAttempt: RetryAttempt context manager

    """
    success = False

    def succeed() -> None:
        nonlocal success
        success = True

    attempt = RetryAttempt(succeed, max_attempts, exceptions_handlers)
    for i in range(max_attempts + 1):
        yield attempt
        if success:
            break
        time.sleep(delay)


async def aretry(
    max_attempts: int = DEFAULT_RETRIES_MAX_ATTEMPTS,
    delay: float = DEFAULT_RETRY_DELAY_SECONDS,
    exceptions_handlers: typing.Optional[ExceptionHandlers] = None,
) -> typing.AsyncGenerator[RetryAttempt, None]:
    """Async Retry a piece of code in case of certain exceptions

    Args:
        max_attempts (int): do retry this times
        delay (float): delay between attempts
        exceptions_handlers (Optional[ExceptionHandlers]): dict with exceptions and their handlers

    Yields:
        RetryAttempt: RetryAttempt context manager

    """
    success = False

    def succeed() -> None:
        nonlocal success
        success = True

    attempt = RetryAttempt(succeed, max_attempts, exceptions_handlers)
    for i in range(max_attempts + 1):
        yield attempt
        if success:
            break

        await asyncio.sleep(delay)
