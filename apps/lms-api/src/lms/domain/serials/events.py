from __future__ import annotations

from dataclasses import dataclass

from lms.domain import DomainEvent


@dataclass
class SerialCreatedEvent(DomainEvent):
    serial_id: str
    item_id: str
    issn: str | None
    frequency: str | None


@dataclass
class SerialActivatedEvent(DomainEvent):
    serial_id: str
    item_id: str


@dataclass
class SerialDeactivatedEvent(DomainEvent):
    serial_id: str
    item_id: str


@dataclass
class SerialIssueReceivedEvent(DomainEvent):
    serial_issue_id: str
    serial_id: str
    item_id: str
    copy_id: str | None
