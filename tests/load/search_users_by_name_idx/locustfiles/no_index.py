import locust

from tests.load.search_users_by_name_idx.locustfiles import base


@locust.events.test_start.add_listener
def setup(environment, **kwargs):
    base.BaseSetupTeardown().setup()


class SearchShape(base.BaseSearchShape): ...


class SearchUser(base.BaseSearchUser):
    """
    Тестируем поиск без индексов
    """
