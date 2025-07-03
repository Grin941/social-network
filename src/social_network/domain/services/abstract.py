import abc
import logging

from src.social_network.database import uow


class AbstractService(abc.ABC):
    def __init__(
        self,
        unit_of_work: uow.UnitOfWork,
        logger: logging.Logger,
    ) -> None:
        self._uow = unit_of_work
        self._logger = logger
