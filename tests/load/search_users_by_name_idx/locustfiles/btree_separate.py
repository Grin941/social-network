import locust

from tests.load.search_users_by_name_idx.locustfiles import base


@locust.events.test_start.add_listener
def setup(environment, **kwargs):
    SetupTeardown().setup()


@locust.events.test_stop.add_listener
def teardown(environment, **kwargs):
    SetupTeardown().teardown()


class SearchShape(base.BaseSearchShape): ...


class SetupTeardown(base.BaseSetupTeardown):
    async def _make_indexes(self) -> None:
        self._logger.info("Making B-tree indexes")
        async for transaction in self._uow.transaction():
            await transaction.execute_raw_query(
                "CREATE EXTENSION IF NOT EXISTS pageinspect;"
            )
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
            await transaction.execute_raw_query("DROP EXTENSION IF EXISTS pageinspect;")

    def setup(self) -> None:
        self._run_async(self._make_indexes())
        self._run_async(self._create_users())

    def teardown(self) -> None:
        self._run_async(self._drop_indexes())


class SearchUser(base.BaseSearchUser):
    """
    Тестируем поиск с двумя отдельными b-tree индексами
    """
