from __future__ import annotations

from datetime import date
from dataclasses import dataclass

from .. import DomainEvent


@dataclass
class AcquisitionOrderCreatedEvent(DomainEvent):
    acquisition_order_id: str


@dataclass
class AcquisitionOrderSubmittedEvent(DomainEvent):
    acquisition_order_id: str


@dataclass
class AcquisitionOrderReceivedEvent(DomainEvent):
    acquisition_order_id: str
    vendor_id: str
    staff_id: str
    item_lines: list[tuple[str, int]]  # [(item_id, quantity)]
    acquisition_date: date


@dataclass
class AcquisitionOrderCancelledEvent(DomainEvent):
    acquisition_order_id: str


@dataclass
class AcquisitionOrderLineAddedEvent(DomainEvent):
    acquisition_order_id: str
    order_line_id: str


@dataclass
class AcquisitionOrderLineRemovedEvent(DomainEvent):
    acquisition_order_id: str
    order_line_id: str


@dataclass
class AcquisitionOrderLineReceivedEvent(DomainEvent):
    acquisition_order_id: str
    order_line_id: str
    quantity: int
    received_quantity: int


@dataclass
class VendorRegisteredEvent(DomainEvent):
    vendor_id: str
    staff_id: str


@dataclass
class VendorUpdatedEvent(DomainEvent):
    vendor_id: str
