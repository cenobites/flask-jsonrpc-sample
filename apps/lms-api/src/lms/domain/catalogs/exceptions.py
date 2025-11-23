from __future__ import annotations

from .. import DomainError, DomainDoesNotExistError


class ItemBaseError(DomainError):
    pass


class ItemDoesNotExistError(DomainDoesNotExistError):
    pass
