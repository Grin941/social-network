import typing

from social_network import exceptions


class DatabaseError(exceptions.SocialNetworkError):
    suffix = "DB"


class NoSessionError(DatabaseError):
    code = 1


class SessionCreationError(DatabaseError):
    code = 2


class ObjectDoesNotExistError(DatabaseError):
    code = 3

    def __init__(self, model: str, id_: typing.Any) -> None:
        self._model = model
        self._id = id_

        super().__init__(message=f"{self._model} with pk {self._id} does not exist")


class ObjectAlreadyExistsError(DatabaseError):
    code = 4

    def __init__(self, model: str, filters: dict[str, typing.Any]) -> None:
        self._model = model
        self._filters = filters

        super().__init__(
            message=f"{self._model} with fields {self._filters} already exists"
        )


class RelatedObjectDoesNotExistError(DatabaseError):
    code = 5

    def __init__(self, model: str, fk_model: str, fk_value: typing.Any) -> None:
        self._model = model
        self._fk_model = fk_model
        self._fk_value = fk_value

        super().__init__(
            message=f"{self._model} FK Object '{self._fk_model}' with value {self._fk_value} does not exist"
        )
