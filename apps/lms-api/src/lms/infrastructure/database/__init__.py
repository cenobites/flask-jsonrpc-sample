from lms.infrastructure import InfrastructureError


class RepositoryError(InfrastructureError):
    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause
