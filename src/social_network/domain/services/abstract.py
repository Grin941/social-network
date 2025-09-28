import abc

from social_network.infrastructure.database import uow


class AbstractService(abc.ABC):
    def __init__(
        self,
        unit_of_work: uow.AbstractUnitOfWork,
    ) -> None:
        self._uow = unit_of_work
