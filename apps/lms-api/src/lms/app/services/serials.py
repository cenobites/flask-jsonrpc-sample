from __future__ import annotations

from lms.domain.serials.entities import Serial
from lms.domain.catalogs.entities import Item
from lms.infrastructure.event_bus import event_bus
from lms.domain.serials.repositories import SerialRepository, SerialIssueRepository
from lms.domain.catalogs.repositories import ItemRepository


class SerialService:
    def __init__(
        self,
        /,
        *,
        serial_repository: SerialRepository,
        serial_issue_repository: SerialIssueRepository,
        item_repository: ItemRepository,
    ) -> None:
        self.serial_repository = serial_repository
        self.serial_issue_repository = serial_issue_repository
        self.item_repository = item_repository

    def _get_item(self, item_id: str) -> Item:
        item = self.item_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f'Item with id {item_id} not found')
        return item

    def _get_serial(self, serial_id: str) -> Serial:
        serial = self.serial_repository.get_by_id(serial_id)
        if not serial:
            raise ValueError(f'Serial with id {serial_id} not found')
        return serial

    def find_all_serials(self) -> list[Serial]:
        return self.serial_repository.find_all()

    def get_serial(self, serial_id: str) -> Serial:
        return self._get_serial(serial_id)

    def subscribe_serial(
        self, title: str, issn: str, item_id: str, frequency: str | None = None, description: str | None = None
    ) -> Serial:
        item = self._get_item(item_id)
        serial = Serial.create(item=item, title=title, issn=issn, frequency=frequency, description=description)
        created_serial = self.serial_repository.save(serial)
        event_bus.publish_events()
        return created_serial

    def renew_serial_subscription(self, serial_id: str) -> Serial:
        serial = self._get_serial(serial_id)
        serial.activate()
        updated_serial = self.serial_repository.save(serial)
        event_bus.publish_events()
        return updated_serial

    def unsubscribe_serial(self, serial_id: str) -> Serial:
        serial = self._get_serial(serial_id)
        serial.deactivate()
        updated_serial = self.serial_repository.save(serial)
        event_bus.publish_events()
        return updated_serial
