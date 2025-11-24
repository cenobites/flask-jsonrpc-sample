from __future__ import annotations

from lms.domain import DomainError


class SerialAlreadyActive(DomainError):
    pass


class SerialAlreadyInactive(DomainError):
    pass
