class SocialNetworkError(Exception):
    code: int = 0
    suffix: str = "SN"

    def __init__(self, message: str) -> None:
        self._message = message

    def __str__(self) -> str:
        return f"{self.suffix}{self.code}: {self._message}"
