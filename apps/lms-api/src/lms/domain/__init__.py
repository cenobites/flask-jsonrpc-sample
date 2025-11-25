from __future__ import annotations

import uuid
import datetime
from dataclasses import field, dataclass


class DomainError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DomainNotFound(DomainError):
    def __init__(self, domain_name: str, domain_id: str) -> None:
        super().__init__(f'{domain_name} with ID {domain_id} was not found')
        self.domain_name = domain_name
        self.domain_id = domain_id


@dataclass
class DomainEntity:
    id: str | None

    def __post_init__(self) -> None:
        if self.id is None:
            self.id = str(uuid.uuid7())


@dataclass
class DomainEvent:
    event_id: str = field(init=False)
    occurred_on: datetime.datetime = field(init=False)

    def __post_init__(self) -> None:
        self.event_id = str(uuid.uuid7())
        self.occurred_on = datetime.datetime.now(datetime.UTC)
