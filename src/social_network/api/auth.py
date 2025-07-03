from starlette import requests
from src.social_network.api import services
from src.social_network.domain.models import user
from fastapi import security
import fastapi
import typing

token = typing.Annotated[
    str, fastapi.Depends(security.OAuth2PasswordBearer(tokenUrl="login"))
]


async def verify_access_token(
    request: requests.Request, auth_service: services.AuthService
) -> user.UserDomain:
    return await auth_service.authorize(request.headers.get("Authorization", ""))
