import typing

from social_network.api.models import common

ResponseInfo = dict[typing.Union[int, str], dict[str, typing.Any]]

response_50x: dict[str, typing.Any] = {
    "description": "Ошибка сервера",
    "model": common.ErrorMessage,
    "headers": {
        "Retry-After": {
            "schema": {"type": "integer", "minimum": 0},
            "description": "Время, через которое еще раз нужно сделать запрос",
        }
    },
}


response_400: ResponseInfo = {400: {"description": "Невалидные данные"}}
response_401: ResponseInfo = {401: {"description": "Невалидный токен"}}
response_500: ResponseInfo = {500: response_50x}
response_503: ResponseInfo = {503: response_50x}
