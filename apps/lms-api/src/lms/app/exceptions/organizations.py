from . import ObjectNotFoundFailed


class BranchNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Branch not found')


class StaffNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Staff not found')
