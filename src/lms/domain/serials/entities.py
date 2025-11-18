from __future__ import annotations

import typing as t
import datetime
from dataclasses import field, dataclass

from lms.domain.serials.events import (
    SerialCreatedEvent,
    SerialActivatedEvent,
    SerialDeactivatedEvent,
    SerialIssueReceivedEvent,
)
from lms.domain.catalogs.entities import Copy, Item
from lms.infrastructure.event_bus import event_bus
from lms.infrastructure.database.models.serials import SerialStatus, SerialIssueStatus

from .. import DomainEntity


@dataclass
class Serial(DomainEntity):
    title: str
    issn: str
    item_id: str
    frequency: str | None = None
    description: str | None = None
    status: str = SerialStatus.ACTIVE.value
    issues: list[int] = field(default_factory=list)

    @classmethod
    def create(
        cls: type[Serial],
        /,
        *,
        title: str,
        issn: str,
        item_id: str,
        frequency: str | None = None,
        description: str | None = None,
    ) -> Serial:
        serial = cls(id=None, title=title, issn=issn, item_id=item_id, frequency=frequency, description=description)
        event_bus.add_event(
            SerialCreatedEvent(
                serial_id=t.cast(str, serial.id), issn=serial.issn, item_id=serial.item_id, frequency=serial.frequency
            )
        )
        return serial

    def activate(self) -> None:
        if self.status == SerialStatus.ACTIVE.value:
            raise ValueError('Serial is already active.')
        self.status = SerialStatus.ACTIVE.value
        event_bus.add_event(SerialActivatedEvent(serial_id=t.cast(str, self.id), item_id=self.item_id))

    def deactivate(self) -> None:
        if self.status == SerialStatus.INACTIVE.value:
            raise ValueError('Serial is already inactive.')
        self.status = SerialStatus.INACTIVE.value
        event_bus.add_event(SerialDeactivatedEvent(serial_id=t.cast(str, self.id), item_id=self.item_id))


@dataclass
class SerialIssue(DomainEntity):
    serial_id: str
    copy_id: str | None = None
    issue_number: str | None = None
    date_received: datetime.date = field(default_factory=datetime.date.today)
    status: str = SerialIssueStatus.RECEIVED.value

    @classmethod
    def create(
        cls: type[SerialIssue],
        /,
        *,
        serial_id: str,
        item: Item,
        copy: Copy | None = None,
        issue_number: str | None = None,
    ) -> SerialIssue:
        serial_issue = cls(
            id=None,
            serial_id=serial_id,
            copy_id=copy.id if copy else None,
            issue_number=issue_number,
            date_received=datetime.date.today(),
            status=SerialIssueStatus.RECEIVED.value,
        )
        event_bus.add_event(
            SerialIssueReceivedEvent(
                serial_id=serial_issue.serial_id,
                serial_issue_id=t.cast(str, serial_issue.id),
                item_id=t.cast(str, item.id),
                copy_id=serial_issue.copy_id,
            )
        )
        return serial_issue
