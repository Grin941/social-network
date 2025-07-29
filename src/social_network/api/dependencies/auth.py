import typing

import fastapi
from fastapi import security

from social_network.api.dependencies import services
from social_network.domain.models import user

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="login")


async def verify_access_token(
    auth_service: services.AuthService,
    token: typing.Annotated[str, fastapi.Depends(oauth2_scheme)],
) -> user.UserDomain:
    return await auth_service.authorize(token)


RequestUser = typing.Annotated[user.UserDomain, fastapi.Depends(verify_access_token)]
