from __future__ import annotations

from lms.domain import DomainError
from lms.app.exceptions import ServiceFailed
from lms.app.exceptions.serials import SerialNotFoundError
from lms.app.exceptions.catalogs import ItemNotFoundError
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
            raise ItemNotFoundError(f'Item with id {item_id} not found')
        return item

    def _get_serial(self, serial_id: str) -> Serial:
        serial = self.serial_repository.get_by_id(serial_id)
        if not serial:
            raise SerialNotFoundError(f'Serial with id {serial_id} not found')
        return serial

    def find_all_serials(self) -> list[Serial]:
        return self.serial_repository.find_all()

    def get_serial(self, serial_id: str) -> Serial:
        return self._get_serial(serial_id)

    def subscribe_serial(
        self, title: str, issn: str, item_id: str, frequency: str | None = None, description: str | None = None
    ) -> Serial:
        item = self._get_item(item_id)
        try:
            serial = Serial.create(item=item, title=title, issn=issn, frequency=frequency, description=description)
        except DomainError as e:
            raise ServiceFailed('The serial subscription cannot be created', cause=e) from e
        created_serial = self.serial_repository.save(serial)
        event_bus.publish_events()
        return created_serial

    def renew_serial_subscription(self, serial_id: str) -> Serial:
        serial = self._get_serial(serial_id)
        try:
            serial.activate()
        except DomainError as e:
            raise ServiceFailed('The serial subscription cannot be renewed', cause=e) from e
        updated_serial = self.serial_repository.save(serial)
        event_bus.publish_events()
        return updated_serial

    def unsubscribe_serial(self, serial_id: str) -> Serial:
        serial = self._get_serial(serial_id)
        try:
            serial.deactivate()
        except DomainError as e:
            raise ServiceFailed('The serial subscription cannot be unsubscribed', cause=e) from e
        updated_serial = self.serial_repository.save(serial)
        event_bus.publish_events()
        return updated_serial
