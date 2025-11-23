from __future__ import annotations

import enum
import uuid
import typing as t
from decimal import Decimal
import datetime

from sqlalchemy import DECIMAL, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from ..db import BaseModel

if t.TYPE_CHECKING:
    from .catalogs import ItemModel
    from .organizations import StaffModel


class VendorStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class OrderStatus(enum.Enum):
    PENDING = 'pending'
    SUBMITTED = 'submitted'
    RECEIVED = 'received'
    CANCELLED = 'cancelled'


class OrderLineStatus(enum.Enum):
    PENDING = 'pending'
    RECEIVED = 'received'
    PARTIALLY_RECEIVED = 'partially_received'


class VendorModel(BaseModel):
    __tablename__ = 'vendors'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[VendorStatus] = mapped_column(default=VendorStatus.ACTIVE)

    acquisition_orders: Mapped[list[AcquisitionOrderModel]] = relationship(
        'AcquisitionOrderModel', back_populates='vendor'
    )


class AcquisitionOrderModel(BaseModel):
    __tablename__ = 'acquisition_orders'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('vendors.id'))
    staff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('staff.id'))
    order_date: Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    received_date: Mapped[datetime.date | None]
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING)

    vendor: Mapped[VendorModel] = relationship('VendorModel', back_populates='acquisition_orders')
    staff: Mapped[StaffModel] = relationship('StaffModel', back_populates='acquisition_orders')
    order_lines: Mapped[list[AcquisitionOrderLineModel]] = relationship(
        'AcquisitionOrderLineModel', back_populates='order'
    )


class AcquisitionOrderLineModel(BaseModel):
    __tablename__ = 'acquisition_order_lines'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('acquisition_orders.id'))
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('items.id'))
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    received_quantity: Mapped[int | None]
    status: Mapped[OrderLineStatus] = mapped_column(default=OrderLineStatus.PENDING)

    order: Mapped[AcquisitionOrderModel] = relationship('AcquisitionOrderModel', back_populates='order_lines')
    item: Mapped[ItemModel] = relationship('ItemModel', back_populates='order_lines')
