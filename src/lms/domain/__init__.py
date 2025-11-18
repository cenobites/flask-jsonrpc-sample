from __future__ import annotations

import uuid
import datetime
from dataclasses import field, dataclass


class DomainError(Exception):
    pass


class DomainDoesNotExistError(DomainError):
    pass


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
