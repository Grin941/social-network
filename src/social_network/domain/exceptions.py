from social_network import exceptions


class DomainError(exceptions.SocialNetworkError):
    suffix = "DOMAIN"


class UserAlreadyRegisteredError(DomainError):
    code = 1

    def __init__(self) -> None:
        super().__init__(message="User already exists")


class OnlyAuthorMayUpdatePostError(DomainError):
    code = 2

    def __init__(self, id_: str, author_id: str, user_id: str) -> None:
        super().__init__(
            message=f"User '{user_id}' can not update post '{id_}' written by user '{author_id}'"
        )


class NotFoundError(DomainError):
    suffix = "NOT_FOUND"


class AuthorNotFoundError(NotFoundError):
    code = 1

    def __init__(self, id_: str) -> None:
        super().__init__(message=f"User '{id_}' not found")


class PostNotFoundError(NotFoundError):
    code = 2

    def __init__(self, id_: str) -> None:
        super().__init__(message=f"Post '{id_}' not found")


class FriendNotFoundError(NotFoundError):
    code = 3

    def __init__(self, user_id: str, friend_id: str) -> None:
        super().__init__(
            message=f"User '{user_id}' or his friend '{friend_id}' not found"
        )


class DialogNotFoundError(NotFoundError):
    code = 4

    def __init__(self, user_id: str, friend_id: str) -> None:
        super().__init__(
            message=f"Dialog between user '{user_id}' and his friend '{friend_id}' not found"
        )


class AuthError(DomainError):
    suffix = "AUTH"


class UserNotFoundError(AuthError):
    code = 1

    def __init__(self, id_: str) -> None:
        super().__init__(message=f"User '{id_}' not found")


class InvalidTokenError(AuthError):
    code = 2

    def __init__(self, token: str) -> None:
        super().__init__(message=f"Token is invalid: {token}")


class WrongPasswordError(AuthError):
    code = 3

    def __init__(self) -> None:
        super().__init__(message="Wrong password")


class TokenIsExpired(AuthError):
    code = 4

    def __init__(self, token: str) -> None:
        super().__init__(message=f"Token {token} is expired")


class FernetKeyError(AuthError):
    code = 5

    def __init__(self) -> None:
        super().__init__(message="Fernet key must be 32 url-safe base64-encoded bytes")


class FernetInvalidTokenError(AuthError):
    code = 6

    def __init__(self, message: str) -> None:
        super().__init__(message=message)
