from src.social_network.infrastructure.database.schema_mappers import abstract_mapper
from src.social_network.infrastructure.database import orm
from src.social_network.application import domain

class UserMapper(abstract_mapper.AbstractMapper[domain.UserDomain, orm.UserORM]):
    @staticmethod
    def map_domain_to_orm(domain_model: domain.UserDomain) -> orm.UserORM:
        return orm.UserORM(
            id=domain_model.id,
            first_name=domain_model.first_name,
            second_name=domain_model.second_name,
            birdth_date=domain_model.birdth_date,
            biography=domain_model.biography,
            city=domain_model.city,
            sex=domain_model.sex,
        )


    @staticmethod
    def map_orm_to_domain(orm_model: orm.UserORM) -> domain.UserDomain:
        return domain.UserDomain(
            id=orm_model.id,
            first_name=orm_model.first_name,
            second_name=orm_model.second_name,
            birdth_date=orm_model.birdth_date,
            biography=orm_model.biography,
            city=orm_model.city,
            sex=orm_model.sex,
        )
