from __future__ import annotations

from decimal import Decimal

from lms.infrastructure.event_bus import event_bus
from lms.domain.acquisitions.entities import Vendor, AcquisitionOrder
from lms.domain.acquisitions.repositories import (
    VendorRepository,
    AcquisitionOrderRepository,
    AcquisitionOrderLineRepository,
)


class AcquisitionOrderService:
    def __init__(
        self,
        /,
        *,
        acquisition_order_repository: AcquisitionOrderRepository,
        acquisition_order_line_repository: AcquisitionOrderLineRepository,
    ) -> None:
        self.acquisition_order_repository = acquisition_order_repository
        self.acquisition_order_line_repository = acquisition_order_line_repository

    def _get_order(self, order_id: str) -> AcquisitionOrder:
        order = self.acquisition_order_repository.get_by_id(order_id)
        if order is None:
            raise ValueError(f'Acquisition order with id {order_id} not found')
        return order

    def find_all_orders(self) -> list[AcquisitionOrder]:
        return self.acquisition_order_repository.find_all()

    def get_order(self, order_id: str) -> AcquisitionOrder:
        return self._get_order(order_id)

    def create_order(self, vendor_id: str, staff_id: str) -> AcquisitionOrder:
        order = AcquisitionOrder.create(vendor_id=vendor_id, staff_id=staff_id)
        created_order = self.acquisition_order_repository.save(order)
        event_bus.publish_events()
        return created_order

    def add_line_to_order(self, order_id: str, item_id: str, quantity: int, unit_price: Decimal) -> AcquisitionOrder:
        order = self.acquisition_order_repository.get_by_id(order_id)
        if order is None:
            raise ValueError(f'Acquisition order with id {order_id} not found')
        order.add_line(item_id=item_id, unit_price=unit_price, quantity=quantity)
        updated_order = self.acquisition_order_repository.save(order)
        event_bus.publish_events()
        return updated_order

    def remove_line_from_order(self, order_id: str, order_line_id: str) -> AcquisitionOrder:
        order = self.acquisition_order_repository.get_by_id(order_id)
        if order is None:
            raise ValueError(f'Acquisition order with id {order_id} not found')
        order.remove_line(order_line_id=order_line_id)
        updated_order = self.acquisition_order_repository.save(order)
        event_bus.publish_events()
        return updated_order

    def receive_line_from_order(
        self, order_id: str, order_line_id: str, received_quantity: int | None = None
    ) -> AcquisitionOrder:
        order = self._get_order(order_id)
        order.receive_line(order_line_id=order_line_id, received_quantity=received_quantity)
        updated_order = self.acquisition_order_repository.save(order)
        event_bus.publish_events()
        return updated_order

    def submit_order(self, order_id: str) -> AcquisitionOrder:
        order = self._get_order(order_id)
        order.submit()
        updated_order = self.acquisition_order_repository.save(order)
        event_bus.publish_events()
        return updated_order

    def cancel_order(self, order_id: str) -> AcquisitionOrder:
        order = self._get_order(order_id)
        order.mark_as_cancelled()
        updated_order = self.acquisition_order_repository.save(order)
        event_bus.publish_events()
        return updated_order


class VendorService:
    def __init__(self, /, *, vendor_repository: VendorRepository) -> None:
        self.vendor_repository = vendor_repository

    def _get(self, vendor_id: str) -> Vendor:
        model = self.vendor_repository.get_by_id(vendor_id)
        if not model:
            raise ValueError(f'Vendor with id {vendor_id} not found')
        return model

    def find_all_vendors(self) -> list[Vendor]:
        return self.vendor_repository.find_all()

    def get_vendor(self, vendor_id: str) -> Vendor:
        return self._get(vendor_id)

    def register_vendor(
        self, name: str, staff_id: str, address: str | None = None, email: str | None = None, phone: str | None = None
    ) -> Vendor:
        vendor = Vendor.create(name=name, staff_id=staff_id, address=address, email=email, phone=phone)
        created_vendor = self.vendor_repository.save(vendor)
        event_bus.publish_events()
        return created_vendor

    def update_vendor(
        self,
        vendor_id: str,
        *,
        name: str | None = None,
        address: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> Vendor:
        vendor = self._get(vendor_id)
        vendor.name = name if name is not None else vendor.name
        vendor.address = address if address is not None else vendor.address
        vendor.email = email if email is not None else vendor.email
        vendor.phone = phone if phone is not None else vendor.phone
        updated_vendor = self.vendor_repository.save(vendor)
        event_bus.publish_events()
        return updated_vendor
