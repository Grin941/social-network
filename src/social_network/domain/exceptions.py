from social_network import exceptions


class DomainError(exceptions.SocialNetworkError):
    suffix = "DOMAIN"


class UserAlreadyRegisteredError(DomainError):
    code = 1

    def __init__(self) -> None:
        super().__init__(message="User already exists")


class AuthError(DomainError):
    suffix = "AUTH"


class UserNotFoundError(AuthError):
    code = 2

    def __init__(self, id_: str) -> None:
        super().__init__(message=f"User '{id_}' not found")


class InvalidTokenError(AuthError):
    code = 3

    def __init__(self, token: str) -> None:
        super().__init__(message=f"Token is invalid: {token}")


class WrongPasswordError(AuthError):
    code = 4

    def __init__(self) -> None:
        super().__init__(message="Wrong password")


class TokenIsExpired(AuthError):
    code = 5

    def __init__(self, token: str) -> None:
        super().__init__(message=f"Token {token} is expired")
