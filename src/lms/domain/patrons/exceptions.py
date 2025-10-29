from __future__ import annotations

from .. import DomainError, DomainDoesNotExistError


class PatronBaseError(DomainError):
    pass


class PatronDoesNotExistError(DomainDoesNotExistError):
    pass


class DuplicatePatronEmailError(PatronBaseError):
    pass


class PatronCannotChangeStatusError(PatronBaseError):
    pass


class PatronCannotBeReinstatedError(PatronBaseError):
    pass


class PatronCannotBorrowError(PatronBaseError):
    pass


class PatronCannotPlaceHoldError(PatronBaseError):
    pass
