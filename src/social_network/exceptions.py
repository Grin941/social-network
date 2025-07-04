class SocialNetworkError(Exception):
    code: int = 0
    suffix: str = ""

    def __init__(self, message: str) -> None:
        self._message = message

    def __str__(self) -> str:
        return f"SN_{self.suffix}_{self.code}: {self._message}"
