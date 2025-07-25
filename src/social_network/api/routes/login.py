import fastapi

from social_network.api import dependencies, responses, models as dto

router = fastapi.APIRouter()


@router.post(
    "/login",
    response_model=dto.TokenDTO,
    response_description="Успешная аутентификация",
    summary="Упрощенный процесс аутентификации",
    description="Упрощенный процесс аутентификации путем передачи идентификатор пользователя и получения токена для дальнейшего прохождения авторизации",
    operation_id="login",
    responses=responses.response_400
    | {404: {"description": "Пользователь не найден"}}
    | responses.response_500
    | responses.response_503,
)
async def login(
    auth_data: dto.AuthDTO, auth_service: dependencies.AuthService
) -> dto.TokenDTO:
    token = await auth_service.login(id_=auth_data.id, password=auth_data.password)
    return dto.TokenDTO(token=token)
