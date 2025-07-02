from src.social_network import exceptions


class DatabaseError(exceptions.SocialNetworkError):
    suffix = "DB"


class NoSessionError(DatabaseError):
    code = 1


class ObjectDoesNotExistError(DatabaseError):
    code = 2

    def __init__(self, model: str, id_: int) -> None:
        self._model = model
        self._id = id_

        super().__init__(message=f"{self._model} with pk {self._id} does not exist")
