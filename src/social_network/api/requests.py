import contextvars
import typing
import uuid

from starlette import requests, responses
from starlette.middleware import base

request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


def get_request_id() -> str:
    return request_id.get(None) or ""


def set_request_id(request_id_to_set: str) -> None:
    request_id.set(request_id_to_set)


def generate_request_id() -> str:
    return str(uuid.uuid4())


class RequestIdMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: requests.Request,
        call_next: typing.Callable[
            [requests.Request], typing.Awaitable[responses.Response]
        ],
    ) -> responses.Response:
        x_request_id: str = request.headers.get(
            "X-Request-ID",
            generate_request_id(),
        )
        set_request_id(x_request_id)

        response: responses.Response = await call_next(request)
        response.headers["X-Request-ID"] = get_request_id()

        return response
