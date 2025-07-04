from social_network.api import services
from social_network.domain.models import user
from fastapi import security
import fastapi
import typing

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="login")


async def verify_access_token(
    auth_service: services.AuthService,
    token: typing.Annotated[str, fastapi.Depends(oauth2_scheme)],
) -> user.UserDomain:
    return await auth_service.authorize(token)
