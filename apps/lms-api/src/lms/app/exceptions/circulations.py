from . import ObjectNotFoundFailed


class LoanNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Loan not found')


class HoldNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Hold not found')
