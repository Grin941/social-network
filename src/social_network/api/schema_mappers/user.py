from social_network.api import models as dto
from social_network.domain import models as domain


class RegistrationMapper:
    @staticmethod
    def map_dto_to_domain(new_user_dto: dto.RegistrationDTO) -> domain.NewUserDomain:
        return domain.NewUserDomain(**new_user_dto.model_dump())

    @staticmethod
    def map_domain_to_dto(user_domain: domain.NewUserDomain) -> dto.RegistrationDTO:
        return dto.RegistrationDTO(
            first_name=user_domain.first_name,
            second_name=user_domain.second_name,
            birthdate=user_domain.birthdate.date(),
            biography=user_domain.biography,
            city=user_domain.city,
            password=user_domain.password,
        )

    @staticmethod
    def map_domain_to_user_dto(user_domain: domain.UserDomain) -> dto.NewUserDTO:
        return dto.NewUserDTO(user_id=user_domain.id)


class UserMapper:
    @staticmethod
    def map_domain_to_dto(user_domain: domain.UserDomain) -> dto.UserDTO:
        return dto.UserDTO(**user_domain.model_dump())
