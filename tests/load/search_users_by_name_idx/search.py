import asyncio

from tests.load import mixin
from tests.load.search_users_by_name_idx import base


class IndexSearchUser(mixin.AsyncMixin, base.BaseSearchUser):
    async def _make_indexes(self) -> None:
        raise NotImplementedError()

    async def _drop_indexes(self) -> None:
        raise NotImplementedError()

    def on_start(self) -> None:
        async def _run() -> None:
            await self._make_indexes()
            await self._create_users()

        self._loop.run_until_complete(self._loop.create_task(_run()))

    def on_stop(self) -> None:
        self._loop.run_until_complete(self._loop.create_task(self._drop_indexes()))


class SearchWithoutIndexesUser(base.BaseSearchUser):
    """
    Тестируем поиск без индексов
    """

    def on_start(self) -> None:
        asyncio.run(self._create_users())


class SearchWithSeparateBtreeIndexesUser(IndexSearchUser):
    """
    Тестируем поиск с двумя отдельными b-tree индексами
    """

    async def _make_indexes(self) -> None:
        self._logger.info("Making B-tree indexes")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS second_name_idx on users(second_name);"
            )
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS first_name_idx on users(first_name);"
            )

    async def _drop_indexes(self) -> None:
        self._logger.info("Removing B-tree indexes")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query("DROP INDEX IF EXISTS second_name_idx;")
            await transaction.execute_raw_query("DROP INDEX IF EXISTS first_name_idx;")


class SearchWithComposedBtreeIndexesUser(IndexSearchUser):
    """
    Тестируем поиск с составным b-tree индексом
    """

    async def _make_indexes(self) -> None:
        self._logger.info("Making composed B-tree index")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS name_idx on users(second_name, first_name);"
            )

    async def _drop_indexes(self) -> None:
        self._logger.info("Removing B-tree index")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query("DROP INDEX IF EXISTS name_idx;")


class SearchWithGinIndexOnLastName(IndexSearchUser):
    """
    Тестируем поиск с GIN индексом только на фамилии
    """

    async def _make_indexes(self) -> None:
        self._logger.info("Making GIN index on the last_name")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
            )
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS second_name_gin_idx ON users USING GIN (second_name gin_trgm_ops);"
            )

    async def _drop_indexes(self) -> None:
        self._logger.info("Removing GIN index")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "DROP INDEX IF EXISTS second_name_gin_idx;"
            )
            await transaction.execute_raw_query("DROP EXTENSION IF EXISTS pg_trgm;")


class SearchWithCompoundGinIndex(IndexSearchUser):
    """
    Тестируем поиск с составным GIN индексом
    """

    async def _make_indexes(self) -> None:
        self._logger.info("Making compound GIN index")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
            )
            await transaction.execute_raw_query(
                "CREATE EXTENSION IF NOT EXISTS btree_gin;"
            )
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS name_gin_idx ON users USING GIN (second_name, first_name gin_trgm_ops);"
            )

    async def _drop_indexes(self) -> None:
        self._logger.info("Removing compound GIN index")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query("DROP INDEX IF EXISTS name_gin_idx;")
            await transaction.execute_raw_query("DROP EXTENSION IF EXISTS btree_gin;")
            await transaction.execute_raw_query("DROP EXTENSION IF EXISTS pg_trgm;")


class SearchWithSeparateGinIndexes(IndexSearchUser):
    """
    Тестируем поиск с двумя отдельными GIN-индексами
    """

    async def _make_indexes(self) -> None:
        self._logger.info("Making two separate GIN indexes")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
            )
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS first_name_gin_idx ON users USING GIN (first_name gin_trgm_ops);"
            )
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS second_name_gin_idx ON users USING GIN (second_name gin_trgm_ops);"
            )

    async def _drop_indexes(self) -> None:
        self._logger.info("Removing GIN indexes")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "DROP INDEX IF EXISTS first_name_gin_idx;"
            )
            await transaction.execute_raw_query(
                "DROP INDEX IF EXISTS second_name_gin_idx;"
            )
            await transaction.execute_raw_query("DROP EXTENSION IF EXISTS pg_trgm;")


class SearchWithSeparateGistIndexes(IndexSearchUser):
    """
    Тестируем поиск с двумя отдельными GIST-индексами
    """

    async def _make_indexes(self) -> None:
        self._logger.info("Making two separate GIST indexes")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
            )
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS first_name_gist_idx ON users USING GIST (first_name gist_trgm_ops);"
            )
            await transaction.execute_raw_query(
                "CREATE INDEX IF NOT EXISTS second_name_gist_idx ON users USING GIST (second_name gist_trgm_ops);"
            )

    async def _drop_indexes(self) -> None:
        self._logger.info("Removing GIST indexes")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "DROP INDEX IF EXISTS first_name_gist_idx;"
            )
            await transaction.execute_raw_query(
                "DROP INDEX IF EXISTS second_name_gist_idx;"
            )
            await transaction.execute_raw_query("DROP EXTENSION IF EXISTS pg_trgm;")
