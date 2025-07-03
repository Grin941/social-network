import fastapi
import typing

from social_network.api.models import (
    registration as registration_dto,
    common,
    user as user_dto,
)
from social_network.domain.models import user as user_domain
from social_network.api import services, auth


router = fastapi.APIRouter(prefix="/user")


@router.post(
    "/register",
    response_model=registration_dto.NewUserDTO,
    response_description="Успешная регистрация",
    summary="Регистрация нового пользователя",
    description="Регистрация нового пользователя",
    operation_id="register_user",
    responses={
        400: {"description": "Невалидные данные", "model": common.ErrorMessage},
        500: {"description": "Ошибка сервера", "model": common.ErrorMessage},
        503: {"description": "Ошибка сервера", "model": common.ErrorMessage},
    },
)
async def login(
    new_user: registration_dto.RegistrationDTO, auth_service: services.AuthService
) -> registration_dto.NewUserDTO:
    user = await auth_service.register(
        user_domain.NewUserDomain(**new_user.model_dump())
    )
    return registration_dto.NewUserDTO(user_id=user.id)


@router.get(
    "/get/{id}",
    response_model=user_dto.UserDTO,
    response_description="Успешное получение анкеты пользователя",
    summary="Получение анкеты пользователяя",
    description="Получение анкеты пользователя",
    operation_id="get_user",
    responses={
        400: {"description": "Невалидные данные", "model": common.ErrorMessage},
        401: {"description": "Невалидный токен", "model": common.ErrorMessage},
        404: {"description": "Анкета не найдена", "model": common.ErrorMessage},
        500: {"description": "Ошибка сервера", "model": common.ErrorMessage},
        503: {"description": "Ошибка сервера", "model": common.ErrorMessage},
    },
    dependencies=[fastapi.Depends(auth.verify_access_token)],
)
async def get_user(
    id: typing.Annotated[str, fastapi.Path(title="Идентификатор пользователя")],
    user_service: services.UserService,
) -> user_dto.UserDTO:
    user = await user_service.get_user(id)
    return user_dto.UserDTO(**user.model_dump())
