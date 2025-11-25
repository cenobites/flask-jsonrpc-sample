from __future__ import annotations

import typing as t
from decimal import Decimal
import datetime
from dataclasses import field, dataclass

from lms.domain import DomainEntity, DomainNotFound
from lms.infrastructure.event_bus import event_bus
from lms.infrastructure.database.models.acquisitions import OrderStatus, VendorStatus, OrderLineStatus

from .events import (
    VendorRegisteredEvent,
    AcquisitionOrderCreatedEvent,
    AcquisitionOrderReceivedEvent,
    AcquisitionOrderCancelledEvent,
    AcquisitionOrderLineAddedEvent,
    AcquisitionOrderSubmittedEvent,
    AcquisitionOrderLineRemovedEvent,
    AcquisitionOrderLineReceivedEvent,
)
from .exceptions import (
    VendorAlreadyActive,
    VendorAlreadyInactive,
    AcquisitionOrderHasNoLines,
    AcquisitionOrderNotPending,
    AcquisitionOrderLineNotSubmitted,
    AcquisitionOrderLineAlreadyReceived,
)


@dataclass
class AcquisitionOrder(DomainEntity):
    vendor_id: str
    staff_id: str
    order_date: datetime.date = field(default_factory=datetime.date.today)
    received_date: datetime.date | None = None
    status: str = OrderStatus.PENDING.value
    order_lines: list[AcquisitionOrderLine] = field(default_factory=list)

    @classmethod
    def create(cls, /, *, vendor_id: str, staff_id: str) -> AcquisitionOrder:
        order = cls(id=None, vendor_id=vendor_id, staff_id=staff_id)
        event_bus.add_event(AcquisitionOrderCreatedEvent(acquisition_order_id=t.cast(str, order.id)))
        return order

    def add_line(self, item_id: str, unit_price: Decimal, quantity: int) -> None:
        if self.status != OrderStatus.PENDING.value:
            raise AcquisitionOrderNotPending(t.cast(str, self.id))
        order_line = AcquisitionOrderLine.create(
            order_id=t.cast(str, self.id), item_id=item_id, unit_price=unit_price, quantity=quantity
        )
        self.order_lines.append(order_line)
        event_bus.add_event(
            AcquisitionOrderLineAddedEvent(
                acquisition_order_id=t.cast(str, self.id), order_line_id=t.cast(str, order_line.id)
            )
        )

    def remove_line(self, order_line_id: str) -> None:
        line_to_remove = next((line for line in self.order_lines if line.id == order_line_id), None)
        if line_to_remove is None:
            raise DomainNotFound('AcquisitionOrderLine', order_line_id)
        if line_to_remove.is_received():
            raise AcquisitionOrderLineAlreadyReceived(t.cast(str, line_to_remove.id), t.cast(str, self.id))
        self.order_lines.remove(line_to_remove)
        event_bus.add_event(
            AcquisitionOrderLineRemovedEvent(
                acquisition_order_id=t.cast(str, self.id), order_line_id=t.cast(str, line_to_remove.id)
            )
        )

    def receive_line(self, order_line_id: str, received_quantity: int | None) -> None:
        if self.status != OrderStatus.SUBMITTED.value:
            raise AcquisitionOrderLineNotSubmitted(order_line_id, t.cast(str, self.id))
        received_line = next((line for line in self.order_lines if line.id == order_line_id), None)
        if not received_line:
            raise DomainNotFound('AcquisitionOrderLine', order_line_id)
        if received_line.is_fully_received():
            raise AcquisitionOrderLineAlreadyReceived(t.cast(str, received_line.id), t.cast(str, self.id))
        received_line.received(
            received_quantity=received_quantity if received_quantity is not None else received_line.quantity
        )
        event_bus.add_event(
            AcquisitionOrderLineReceivedEvent(
                acquisition_order_id=t.cast(str, self.id),
                order_line_id=t.cast(str, received_line.id),
                quantity=received_line.quantity,
                received_quantity=t.cast(int, received_line.received_quantity),
            )
        )
        if all(line.is_received() for line in self.order_lines):
            self.status = OrderStatus.RECEIVED.value
            self.received_date = datetime.date.today()
            event_bus.add_event(
                AcquisitionOrderReceivedEvent(
                    acquisition_order_id=t.cast(str, self.id),
                    vendor_id=self.vendor_id,
                    staff_id=self.staff_id,
                    item_lines=[(line.item_id, t.cast(int, line.received_quantity)) for line in self.order_lines],
                    acquisition_date=self.received_date,
                )
            )

    def submit(self) -> None:
        if self.status != OrderStatus.PENDING.value:
            raise AcquisitionOrderNotPending(t.cast(str, self.id))
        if not self.order_lines:
            raise AcquisitionOrderHasNoLines(t.cast(str, self.id))
        self.status = OrderStatus.SUBMITTED.value
        event_bus.add_event(AcquisitionOrderSubmittedEvent(acquisition_order_id=t.cast(str, self.id)))

    def mark_as_cancelled(self) -> None:
        if self.status != OrderStatus.PENDING.value:
            raise AcquisitionOrderNotPending(t.cast(str, self.id))
        self.status = OrderStatus.CANCELLED.value
        event_bus.add_event(AcquisitionOrderCancelledEvent(acquisition_order_id=t.cast(str, self.id)))


@dataclass
class AcquisitionOrderLine(DomainEntity):
    order_id: str
    item_id: str
    unit_price: Decimal
    quantity: int = 1
    received_quantity: int | None = None
    status: str = OrderLineStatus.PENDING.value

    @classmethod
    def create(cls, /, *, order_id: str, item_id: str, unit_price: Decimal, quantity: int = 1) -> AcquisitionOrderLine:
        return cls(id=None, order_id=order_id, item_id=item_id, unit_price=unit_price, quantity=quantity)

    def is_received(self) -> bool:
        return self.status in (OrderLineStatus.RECEIVED.value, OrderLineStatus.PARTIALLY_RECEIVED.value)

    def is_fully_received(self) -> bool:
        return self.received_quantity is not None and self.received_quantity >= self.quantity

    def received(self, /, *, received_quantity: int) -> None:
        self.received_quantity = received_quantity
        self.status = (
            OrderLineStatus.RECEIVED.value if self.is_fully_received() else OrderLineStatus.PARTIALLY_RECEIVED.value
        )


@dataclass
class Vendor(DomainEntity):
    name: str
    address: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str = VendorStatus.ACTIVE.value

    @classmethod
    def create(
        cls,
        /,
        *,
        name: str,
        staff_id: str,
        address: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> Vendor:
        vendor = cls(id=None, name=name, address=address, email=email, phone=phone)
        event_bus.add_event(VendorRegisteredEvent(vendor_id=t.cast(str, vendor.id), staff_id=staff_id))
        return vendor

    def activate(self) -> None:
        if self.status == VendorStatus.ACTIVE.value:
            raise VendorAlreadyActive(t.cast(str, self.id))
        self.status = VendorStatus.ACTIVE.value

    def deactivate(self) -> None:
        if self.status == VendorStatus.INACTIVE.value:
            raise VendorAlreadyInactive(t.cast(str, self.id))
        self.status = VendorStatus.INACTIVE.value
