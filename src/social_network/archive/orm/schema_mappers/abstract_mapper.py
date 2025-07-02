import abc
import typing

DomainModel = typing.TypeVar("DomainModel")
ORMModel = typing.TypeVar("ORMModel")


class AbstractMapper(abc.ABC, typing.Generic[DomainModel, ORMModel]):
    @staticmethod
    @abc.abstractmethod
    def map_domain_to_orm(domain_model: DomainModel) -> ORMModel: ...

    @staticmethod
    @abc.abstractmethod
    def map_orm_to_domain(orm_model: ORMModel) -> DomainModel: ...
