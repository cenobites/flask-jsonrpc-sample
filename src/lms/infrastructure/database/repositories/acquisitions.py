from __future__ import annotations

import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.acquisitions.entities import Vendor, AcquisitionOrder, AcquisitionOrderLine
from lms.infrastructure.database.models.acquisitions import (
    OrderStatus,
    VendorModel,
    AcquisitionOrderModel,
    AcquisitionOrderLineModel,
)
from lms.infrastructure.database.mappers.acquisitions import (
    VendorMapper,
    AcquisitionOrderMapper,
    AcquisitionOrderLineMapper,
)


class SQLAlchemyAcquisitionOrderRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[AcquisitionOrder]:
        models = self.session.query(AcquisitionOrderModel).all()
        return [AcquisitionOrderMapper.to_entity(m) for m in models]

    def get_by_id(self, order_id: str) -> AcquisitionOrder | None:
        model = self.session.get(AcquisitionOrderModel, order_id)
        return AcquisitionOrderMapper.to_entity(model) if model else None

    def save(self, order: AcquisitionOrder) -> AcquisitionOrder:
        model = self.session.get(AcquisitionOrderModel, order.id) if order.id else None
        if not model:
            model = AcquisitionOrderMapper.from_entity(order)
            self.session.add(model)
            self.session.commit()
            order.id = str(model.id)
            return order
        model.received_date = order.received_date
        model.status = OrderStatus(order.status)

        for line_model in model.order_lines:
            self.session.delete(line_model)
        model.order_lines = [AcquisitionOrderLineMapper.from_entity(line) for line in order.order_lines]
        self.session.commit()
        for line, line_model in zip(order.order_lines, model.order_lines, strict=True):
            line.id = str(line_model.id)
        return order


class SQLAlchemyAcquisitionOrderLineRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_by_order(self, order_id: str) -> list[AcquisitionOrderLine]:
        models = self.session.query(AcquisitionOrderLineModel).filter_by(order_id=order_id).all()
        return [AcquisitionOrderLineMapper.to_entity(m) for m in models]

    def get_by_id(self, order_line_id: str) -> AcquisitionOrderLine | None:
        model = self.session.get(AcquisitionOrderLineModel, order_line_id)
        return AcquisitionOrderLineMapper.to_entity(model) if model else None


class SQLAlchemyVendorRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Vendor]:
        models = self.session.query(VendorModel).all()
        return [VendorMapper.to_entity(m) for m in models]

    def get_by_id(self, vendor_id: str) -> Vendor | None:
        model = self.session.get(VendorModel, vendor_id)
        return VendorMapper.to_entity(model) if model else None

    def save(self, vendor: Vendor) -> Vendor:
        model = self.session.get(VendorModel, vendor.id) if vendor.id else None
        if not model:
            model = VendorMapper.from_entity(vendor)
            self.session.add(model)
            self.session.commit()
            vendor.id = str(model.id)
            return vendor
        model.name = vendor.name
        model.address = vendor.address
        model.email = vendor.email
        model.phone = vendor.phone
        self.session.commit()
        return vendor
