from __future__ import annotations

from .. import DomainError, DomainDoesNotExistError


class OrderBaseError(DomainError):
    pass


class OrderDoesNotExistError(DomainDoesNotExistError):
    pass
