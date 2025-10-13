import abc
import json
import typing
import uuid

import aio_pika
import pydantic

from social_network.infrastructure.database import uow


class AbstractService(abc.ABC):
    def __init__(
        self,
        unit_of_work: uow.AbstractUnitOfWork,
    ) -> None:
        self._uow = unit_of_work


class AbstractAsyncService(abc.ABC):
    def __init__(
        self,
        exchange: typing.Optional[aio_pika.abc.AbstractRobustExchange],
        channel: typing.Optional[aio_pika.abc.AbstractChannel],
    ) -> None:
        self._exchange = exchange
        self._channel = channel

    @classmethod
    @abc.abstractmethod
    async def create(
        cls, rmq_chanel: aio_pika.abc.AbstractRobustChannel
    ) -> "AbstractAsyncService": ...

    @abc.abstractmethod
    async def bind(
        self, user_id: uuid.UUID
    ) -> typing.Optional[aio_pika.abc.AbstractQueue]: ...

    @abc.abstractmethod
    async def publish(
        self, data: pydantic.BaseModel, to: typing.Optional[uuid.UUID] = None
    ) -> None: ...

    @staticmethod
    async def process_message(
        msg: aio_pika.abc.AbstractIncomingMessage,
        callback: typing.Callable[[dict[str, typing.Any]], typing.Any],
    ) -> None:
        """
        Обрабатываем сообщение и в случае, если корутина выполнилась неудачно,
        возвращаем сообщение в очередь
        """
        async with msg.process(ignore_processed=True):
            try:
                context = json.loads(msg.body.decode())
                _ = await callback(context)
                # при успешном выполнении callback ожидаем получить True
                if not _:
                    # возвращаем сообщение обратно в очередь
                    await msg.nack()
            except Exception:
                # возвращаем сообщение обратно в очередь
                await msg.nack()
                raise
