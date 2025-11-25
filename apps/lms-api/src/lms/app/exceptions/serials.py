from . import ObjectNotFoundFailed


class SerialNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Serial not found')


class SerialIssueNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Serial issue not found')
