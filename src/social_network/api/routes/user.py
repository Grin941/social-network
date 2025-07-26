import fastapi
import typing

from social_network.api import dependencies, responses, schema_mappers, models as dto

router = fastapi.APIRouter(prefix="/user")


@router.post(
    "/register",
    response_model=dto.NewUserDTO,
    response_description="Успешная регистрация",
    summary="Регистрация нового пользователя",
    description="Регистрация нового пользователя",
    operation_id="register_user",
    responses=responses.response_400 | responses.response_500 | responses.response_503,
)
async def register(
    new_user: dto.RegistrationDTO, auth_service: dependencies.AuthService
) -> dto.NewUserDTO:
    user = await auth_service.register(
        schema_mappers.RegistrationMapper.map_dto_to_domain(new_user)
    )
    return schema_mappers.RegistrationMapper.map_domain_to_dto(user)


@router.get(
    "/get/{id}",
    response_model=dto.UserDTO,
    response_description="Успешное получение анкеты пользователя",
    summary="Получение анкеты пользователя",
    description="Получение анкеты пользователя",
    operation_id="get_user",
    responses=responses.response_400
    | responses.response_401
    | {404: {"description": "Анкета не найдена"}}
    | responses.response_500
    | responses.response_503,
    dependencies=[fastapi.Depends(dependencies.verify_access_token)],
)
async def get_user(
    id: typing.Annotated[str, fastapi.Path(title="Идентификатор пользователя")],
    user_service: dependencies.UserService,
) -> dto.UserDTO:
    user = await user_service.get_user(id)
    return schema_mappers.UserMapper.map_domain_to_dto(user)
