import asyncio
import datetime
import functools
import json
import logging
import typing
import uuid

import aio_pika.abc
from redis import asyncio as aioredis

from social_network.api import models as dto
from social_network.domain import models
from social_network.domain.services import abstract
from social_network.infrastructure.database import uow

logger = logging.getLogger(__name__)


def handle_redis_error():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> typing.Any:
            try:
                return await func(*args, **kwargs)
            except aioredis.RedisError:
                pass

        return wrapped

    return wrapper


def handle_rmq_error():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> typing.Any:
            try:
                return await func(*args, **kwargs)
            except aio_pika.exceptions.AMQPError:
                pass

        return wrapped

    return wrapper


class AsyncFeedService(abstract.AbstractAsyncService):
    @classmethod
    async def create(
        cls, rmq_channel: typing.Optional[aio_pika.abc.AbstractRobustChannel]
    ) -> "AsyncFeedService":
        exchange = None
        if rmq_channel:
            exchange = await rmq_channel.declare_exchange(
                "posts_feed", aio_pika.ExchangeType.DIRECT
            )
        self = cls(exchange=exchange, channel=rmq_channel)
        return self

    async def bind(
        self, user_id: uuid.UUID
    ) -> typing.Optional[aio_pika.abc.AbstractQueue]:
        queue = None
        if self._channel and self._exchange:
            queue = await self._channel.declare_queue(
                name=f"feed:{user_id}", durable=True, exclusive=True
            )
            await queue.bind(self._exchange, routing_key=f"feed:{user_id}")
        return queue

    @handle_rmq_error()
    async def publish(
        self, data: models.PostDomain, to: typing.Optional[uuid.UUID] = None
    ) -> None:
        routing_key = "feed"
        if to:
            routing_key = f"{routing_key}:{to}"

        if self._exchange:
            await self._exchange.publish(
                message=aio_pika.Message(
                    json.dumps(
                        dto.PostWsDTO(
                            payload=dto.PostWsPayload(
                                postId=data.id,
                                postText=data.text,
                                author_user_id=data.author_id,
                            )
                        ).model_dump()
                    ).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key,
            )


class FeedService(abstract.AbstractService):
    def __init__(
        self,
        unit_of_work: uow.FeedUnitOfWork,
        redis: aioredis.Redis,
        async_feed_service: AsyncFeedService,
        cache_capacity: int = 1000,
        ttl: int = 600,
        lock_timeout: float = 60.0,
    ) -> None:
        super().__init__(unit_of_work)
        self._async_feed_service = async_feed_service
        self._capacity = cache_capacity
        self._ttl = ttl
        self._lock_timeout = lock_timeout
        self._redis = redis

    @property
    def uow(self) -> uow.FeedUnitOfWork:
        return typing.cast(uow.FeedUnitOfWork, self._uow)

    @staticmethod
    def feed_key(user_id: uuid.UUID) -> str:
        return f"feed:{user_id}"

    @staticmethod
    def lock_key(user_id: uuid.UUID) -> str:
        return f"lock:{user_id}"

    @staticmethod
    def ttl_key(user_id: uuid.UUID) -> str:
        return f"ttl:{user_id}"

    @staticmethod
    def _parse(post: models.PostDomain) -> tuple[str, float]:
        return post.model_dump_json(), post.updated_at.timestamp()

    async def _count(self, user_id) -> int:
        return await self._redis.zcard(self.feed_key(user_id))

    async def _add(self, post: models.PostDomain, user_id: uuid.UUID) -> None:
        data, score = self._parse(post)
        await self._redis.zadd(name=self.feed_key(user_id), mapping={data: score})

    async def _expire(self, user_id: uuid.UUID, ttl: int) -> None:
        await self._redis.set(
            name=self.ttl_key(user_id),
            value=str(
                (
                    datetime.datetime.now(datetime.timezone.utc)
                    + datetime.timedelta(seconds=ttl)
                ).timestamp()
            ),
        )

    async def _is_expired(self, user_id: uuid.UUID) -> bool:
        expiration_ts = await self._redis.get(self.ttl_key(user_id)) or 0
        return datetime.datetime.now(datetime.timezone.utc).timestamp() > float(
            expiration_ts
        )

    async def _invalidate(self, user_id: uuid.UUID) -> None:
        await self._redis.delete(self.feed_key(user_id))

    async def _warm_up(self, user_id: uuid.UUID) -> None:
        logger.info(f"Warming up {self.feed_key(user_id)}")
        posts_count = await self._count(user_id)
        if posts_count:
            await self._redis.delete(self.feed_key(user_id))

        async for _ in self.uow.transaction():
            posts = await self.uow.posts.feed(
                user_id=user_id,
                offset=0,
                limit=self._capacity,
            )
        for post in posts:
            await self._add(post=post, user_id=user_id)
        await self._expire(user_id=user_id, ttl=self._ttl)

    @handle_redis_error()
    async def add_post(self, user_id: uuid.UUID, post: models.PostDomain) -> None:
        async for _ in self.uow.transaction():
            friends = await self.uow.friends.find_all(
                exclude_deleted=True,
                filters={"user_id": user_id},
            )
        for friend in friends:
            await self._async_feed_service.publish(data=post, to=friend.id)
            async with self._redis.lock(
                name=self.lock_key(friend.friend_id),
                blocking_timeout=self._lock_timeout,
            ):
                posts_count = await self._count(friend.friend_id)
                if not posts_count:
                    logger.info(
                        f"Cache {self.feed_key(friend.friend_id)} is not warmed up yet. Skip."
                    )
                    continue

                is_expired = await self._is_expired(user_id=friend.friend_id)
                if is_expired:
                    logger.info(
                        f"Cache {self.feed_key(friend.friend_id)} is expired. Warm up"
                    )
                    await self._warm_up(user_id=friend.friend_id)
                    continue

                if extra_feed_posts_count := max(-1, posts_count - self._capacity) + 1:
                    await self._redis.zpopmin(
                        self.feed_key(friend.friend_id), extra_feed_posts_count
                    )

                await self._add(post=post, user_id=friend.friend_id)
                await self._expire(user_id=friend.friend_id, ttl=self._ttl)
                logger.info(
                    f"Added post {post.id} to {self.feed_key(friend.friend_id)}"
                )

    @handle_redis_error()
    async def delete_post(self, user_id: uuid.UUID, post_id: uuid.UUID) -> None:
        async for _ in self.uow.transaction():
            friends, post = await asyncio.gather(
                self.uow.friends.find_all(
                    exclude_deleted=True,
                    filters={"user_id": user_id},
                ),
                self.uow.posts.find_one(str(post_id)),
            )
        for friend in friends:
            async with self._redis.lock(
                name=self.lock_key(friend.friend_id),
                blocking_timeout=self._lock_timeout,
            ):
                await self._invalidate(friend.friend_id)
                logger.info(
                    f"Deleted post {post.id} from {self.feed_key(friend.friend_id)} – invalidated cache"
                )

    @handle_redis_error()
    async def update_post(self, user_id: uuid.UUID, post: models.PostDomain) -> None:
        async for _ in self.uow.transaction():
            friends = await self.uow.friends.find_all(
                exclude_deleted=True,
                filters={"user_id": user_id},
            )
        for friend in friends:
            async with self._redis.lock(
                name=self.lock_key(friend.friend_id),
                blocking_timeout=self._lock_timeout,
            ):
                await self._invalidate(friend.friend_id)
                logger.info(
                    f"Updated post {post.id} from {self.feed_key(friend.friend_id)} – invalidated cache"
                )

    @handle_redis_error()
    async def add_friend(self, user_id: uuid.UUID, friend_id: uuid.UUID) -> None:
        """Нужно удалить из ленты пользователя посты его друзей. Операция редкая – проще инвалидировать кэш"""
        for id_ in (user_id, friend_id):
            async with self._redis.lock(
                name=self.lock_key(id_), blocking_timeout=self._lock_timeout
            ):
                await self._invalidate(id_)
                logger.info(f"Added friend {friend_id} to {id_} – invalidated cache")

    @handle_redis_error()
    async def delete_friend(self, user_id: uuid.UUID, friend_id: uuid.UUID) -> None:
        """
        Нужно удалить из ленты пользователя посты его удаленного друга.
        Операция редкая – проще инвалидировать кэш
        """
        for id_ in (user_id, friend_id):
            async with self._redis.lock(
                name=self.lock_key(id_), blocking_timeout=self._lock_timeout
            ):
                await self._invalidate(id_)
                logger.info(
                    f"Removed friendship between {friend_id} and {id_} – invalidated cache"
                )

    async def feed(
        self, user_id: uuid.UUID, offset: int, limit: int
    ) -> list[models.PostDomain]:
        use_cache = True
        if offset > self._capacity:
            use_cache = False

        posts_from_cache: list[models.PostDomain] = []
        if use_cache:
            logger.info(f"Feed from cache {self.feed_key(user_id)}")
            lock = self._redis.lock(
                name=self.lock_key(user_id), timeout=self._lock_timeout
            )
            lock_acquired = await lock.acquire(blocking=False)
            if lock_acquired:
                posts_count = await self._redis.zcard(self.feed_key(user_id))
                is_expired = await self._is_expired(user_id=user_id)
                if not posts_count or is_expired:
                    await self._warm_up(user_id=user_id)

                cached_posts = await self._redis.zrange(
                    name=self.feed_key(user_id),
                    start=offset,
                    end=offset + limit,
                    desc=True,
                )
                posts_from_cache = [
                    models.PostDomain(**json.loads(post)) for post in cached_posts
                ]
                await lock.release()

        if (
            len(posts_from_cache) < limit
            and len(posts_from_cache) + offset <= self._capacity
        ):
            return posts_from_cache

        if (
            len(posts_from_cache) >= limit
            or self._capacity < len(posts_from_cache) + offset
        ):
            return posts_from_cache[: limit + 1]

        logger.info("Feed from db")
        async for _ in self.uow.transaction():
            posts_from_db = await self.uow.posts.feed(
                user_id=user_id,
                offset=offset + len(posts_from_cache),
                limit=limit - len(posts_from_cache),
            )

        return posts_from_cache + posts_from_db
