import asyncio
import dataclasses
import functools
import typing

import aio_pika.abc
from fastapi import WebSocket

from social_network.domain import models
from social_network.domain.services import abstract


@dataclasses.dataclass
class WSConnection:
    """
    Коннект сокета характеризуется самим сокетом и пользователем.
    Важно, чтобы по соединению информацию о событиях системы
    не мог получать неавторизованный пользователь.
    """

    socket: WebSocket
    queue: typing.Optional[aio_pika.abc.AbstractQueue] = None
    user: typing.Optional[models.UserDomain] = None

    @property
    def is_authorized(self):
        """
        По умолчанию соединение не авторизовано,
        если при его установке системе не был передан токен
        """
        return self.user is not None

    def __eq__(self, other):
        return self.socket == other.socket

    def __hash__(self):
        return hash(self.socket)

    async def send_to_ws(self, message: dict[str, typing.Any]) -> bool:
        if self.is_authorized:
            await self.socket.send_json(message)
            return True
        return False

    async def subscribe(
        self,
        message_processor: typing.Callable[
            [
                aio_pika.abc.AbstractIncomingMessage,
                typing.Callable[[dict[str, typing.Any]], typing.Any],
            ],
            typing.Coroutine[typing.Any, typing.Any, None],
        ],
    ) -> None:
        callback = functools.partial(message_processor, callback=self.send_to_ws)  # type: ignore
        if self.queue:
            await self.queue.consume(callback)
            await asyncio.Future()


class WSConnectionManager:
    """
    Менеджер соединений следит за соединениями вэб-сокетов.
    Соединение можно:
    - создать
    - разорвать
    - можно послать сообщение массово всем открытым авторизованным соединениям
    - можно послать сообщение конкретному авторизованному соединению
    """

    def __init__(self, async_service: abstract.AbstractAsyncService) -> None:
        self._async_service = async_service
        self._connections: set[WSConnection] = set()

    async def connect(self, websocket: WebSocket, user: models.UserDomain) -> None:
        """
        Создаем соединение и добавляем его в
        список открытых соединений
        """
        await websocket.accept()
        queue = await self._async_service.bind(user.id)
        ws_connection = WSConnection(socket=websocket, user=user, queue=queue)
        self._connections.add(ws_connection)
        await ws_connection.subscribe(
            message_processor=self._async_service.process_message
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Удаляем соединение из списка открытых соединений
        """
        ws_connection = WSConnection(socket=websocket)
        self._connections.remove(ws_connection)
