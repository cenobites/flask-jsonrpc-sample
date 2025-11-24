class ApplicationError(Exception):
    def __init__(self, message: str, code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class ServiceFailed(ApplicationError):
    def __init__(self, message: str, code: int = 400, *, cause: Exception | None = None) -> None:
        super().__init__(message=message, code=code)
        self.cause = cause


class ObjectNotFoundFailed(ServiceFailed):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code=404)
