from __future__ import annotations

import uuid

from lms.domain.acquisitions.entities import Vendor, OrderLineStatus, AcquisitionOrder, AcquisitionOrderLine
from lms.infrastructure.database.models.acquisitions import (
    OrderStatus,
    VendorModel,
    AcquisitionOrderModel,
    AcquisitionOrderLineModel,
)


class AcquisitionOrderMapper:
    @staticmethod
    def to_entity(model: AcquisitionOrderModel) -> AcquisitionOrder:
        order_lines = [AcquisitionOrderLineMapper.to_entity(line_model) for line_model in model.order_lines]
        return AcquisitionOrder(
            id=str(model.id) if model.id else None,
            vendor_id=str(model.vendor_id),
            staff_id=str(model.staff_id),
            order_date=model.order_date,
            received_date=model.received_date,
            status=model.status.value,
            order_lines=order_lines,
        )

    @staticmethod
    def from_entity(entity: AcquisitionOrder) -> AcquisitionOrderModel:
        model = AcquisitionOrderModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.vendor_id = uuid.UUID(entity.vendor_id)
        model.staff_id = uuid.UUID(entity.staff_id)
        model.order_date = entity.order_date
        model.received_date = entity.received_date
        model.status = OrderStatus(entity.status)
        model.order_lines = [AcquisitionOrderLineMapper.from_entity(line) for line in entity.order_lines]
        return model


class AcquisitionOrderLineMapper:
    @staticmethod
    def to_entity(model: AcquisitionOrderLineModel) -> AcquisitionOrderLine:
        return AcquisitionOrderLine(
            id=str(model.id) if model.id else None,
            order_id=str(model.order_id),
            item_id=str(model.item_id),
            unit_price=model.unit_price,
            quantity=model.quantity,
            status=model.status.value,
            received_quantity=model.received_quantity,
        )

    @staticmethod
    def from_entity(entity: AcquisitionOrderLine) -> AcquisitionOrderLineModel:
        model = AcquisitionOrderLineModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.order_id = uuid.UUID(entity.order_id)
        model.item_id = uuid.UUID(entity.item_id)
        model.unit_price = entity.unit_price
        model.quantity = entity.quantity
        model.received_quantity = entity.received_quantity
        model.status = OrderLineStatus(entity.status)
        return model


class VendorMapper:
    @staticmethod
    def to_entity(model: VendorModel) -> Vendor:
        return Vendor(
            id=str(model.id) if model.id else None,
            name=model.name,
            address=model.address,
            email=model.email,
            phone=model.phone,
        )

    @staticmethod
    def from_entity(entity: Vendor) -> VendorModel:
        model = VendorModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.name = entity.name
        model.address = entity.address
        model.email = entity.email
        model.phone = entity.phone
        return model
