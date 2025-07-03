import fastapi

from social_network.api.models import auth, common
from social_network.api import services


router = fastapi.APIRouter()


@router.post(
    "/login",
    response_model=auth.TokenDTO,
    response_description="Успешная аутентификация",
    summary="Упрощенный процесс аутентификации",
    description="Упрощенный процесс аутентификации путем передачи идентификатор пользователя и получения токена для дальнейшего прохождения авторизации",
    operation_id="login",
    responses={
        400: {"description": "Невалидные данные", "model": common.ErrorMessage},
        404: {"description": "Пользователь не найден", "model": common.ErrorMessage},
        500: {"description": "Ошибка сервера", "model": common.ErrorMessage},
        503: {"description": "Ошибка сервера", "model": common.ErrorMessage},
    },
)
async def login(
    auth_data: auth.AuthDTO, auth_service: services.AuthService
) -> auth.TokenDTO:
    token = await auth_service.login(id_=auth_data.id, password=auth_data.password)
    return auth.TokenDTO(token=token)
