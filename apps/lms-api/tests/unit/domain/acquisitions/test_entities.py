from __future__ import annotations

from decimal import Decimal
import datetime
from unittest.mock import patch
from collections.abc import Iterator

import pytest

from lms.domain import DomainNotFound
from lms.domain.acquisitions.entities import Vendor, AcquisitionOrder, AcquisitionOrderLine
from lms.domain.acquisitions.exceptions import (
    VendorAlreadyActive,
    VendorAlreadyInactive,
    AcquisitionOrderHasNoLines,
    AcquisitionOrderNotPending,
    AcquisitionOrderLineNotSubmitted,
    AcquisitionOrderLineAlreadyReceived,
)
from lms.infrastructure.database.models.acquisitions import OrderStatus, VendorStatus, OrderLineStatus


@pytest.fixture
def mock_event_bus() -> Iterator:
    with patch('lms.domain.acquisitions.entities.event_bus') as mock_bus:
        yield mock_bus


class TestVendor:
    def test_create_vendor(self, mock_event_bus: object) -> None:
        vendor = Vendor.create(name='Test Vendor', staff_id='staff1', email='test@example.com', phone='123-456-7890')

        assert vendor.name == 'Test Vendor'
        assert vendor.email == 'test@example.com'
        assert vendor.phone == '123-456-7890'
        assert vendor.status == VendorStatus.ACTIVE.value
        mock_event_bus.add_event.assert_called_once()

    def test_create_vendor_minimal(self, mock_event_bus: object) -> None:
        vendor = Vendor.create(name='Minimal Vendor', staff_id='staff1')

        assert vendor.name == 'Minimal Vendor'
        assert vendor.email is None
        assert vendor.phone is None
        assert vendor.status == VendorStatus.ACTIVE.value

    def test_activate_vendor(self, mock_event_bus: object) -> None:
        vendor = Vendor(id='v1', name='Test', status=VendorStatus.INACTIVE.value)

        vendor.activate()

        assert vendor.status == VendorStatus.ACTIVE.value

    def test_activate_already_active_vendor(self, mock_event_bus: object) -> None:
        vendor = Vendor(id='v1', name='Test', status=VendorStatus.ACTIVE.value)

        with pytest.raises(VendorAlreadyActive):
            vendor.activate()

    def test_deactivate_vendor(self, mock_event_bus: object) -> None:
        vendor = Vendor(id='v1', name='Test', status=VendorStatus.ACTIVE.value)

        vendor.deactivate()

        assert vendor.status == VendorStatus.INACTIVE.value

    def test_deactivate_already_inactive_vendor(self, mock_event_bus: object) -> None:
        vendor = Vendor(id='v1', name='Test', status=VendorStatus.INACTIVE.value)

        with pytest.raises(VendorAlreadyInactive):
            vendor.deactivate()


class TestAcquisitionOrderLine:
    def test_create_order_line(self, mock_event_bus: object) -> None:
        line = AcquisitionOrderLine.create(order_id='order1', item_id='item1', unit_price=Decimal('29.99'), quantity=5)

        assert line.order_id == 'order1'
        assert line.item_id == 'item1'
        assert line.unit_price == Decimal('29.99')
        assert line.quantity == 5
        assert line.received_quantity is None
        assert line.status == OrderLineStatus.PENDING.value

    def test_is_received_fully(self, mock_event_bus: object) -> None:
        line = AcquisitionOrderLine(
            id='line1',
            order_id='order1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            received_quantity=5,
            status=OrderLineStatus.RECEIVED.value,
        )

        assert line.is_received() is True
        assert line.is_fully_received() is True

    def test_is_received_partially(self, mock_event_bus: object) -> None:
        line = AcquisitionOrderLine(
            id='line1',
            order_id='order1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            received_quantity=3,
            status=OrderLineStatus.PARTIALLY_RECEIVED.value,
        )

        assert line.is_received() is True
        assert line.is_fully_received() is False

    def test_is_not_received(self, mock_event_bus: object) -> None:
        line = AcquisitionOrderLine(
            id='line1',
            order_id='order1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            received_quantity=0,
            status=OrderLineStatus.PENDING.value,
        )

        assert line.is_received() is False
        assert line.is_fully_received() is False

    def test_received_full_quantity(self, mock_event_bus: object) -> None:
        line = AcquisitionOrderLine(
            id='line1', order_id='order1', item_id='item1', unit_price=Decimal('10.00'), quantity=5, received_quantity=0
        )

        line.received(received_quantity=5)

        assert line.received_quantity == 5
        assert line.status == OrderLineStatus.RECEIVED.value

    def test_received_partial_quantity(self, mock_event_bus: object) -> None:
        line = AcquisitionOrderLine(
            id='line1', order_id='order1', item_id='item1', unit_price=Decimal('10.00'), quantity=5, received_quantity=0
        )

        line.received(received_quantity=3)

        assert line.received_quantity == 3
        assert line.status == OrderLineStatus.PARTIALLY_RECEIVED.value


class TestAcquisitionOrder:
    def test_create_order(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder.create(vendor_id='v1', staff_id='s1')

        assert order.vendor_id == 'v1'
        assert order.staff_id == 's1'
        assert order.status == OrderStatus.PENDING.value
        assert order.order_lines == []
        assert order.received_date is None
        mock_event_bus.add_event.assert_called_once()

    def test_add_line_to_pending_order(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.PENDING.value)

        order.add_line(item_id='item1', unit_price=Decimal('19.99'), quantity=3)

        assert len(order.order_lines) == 1
        assert order.order_lines[0].item_id == 'item1'
        assert order.order_lines[0].unit_price == Decimal('19.99')
        assert order.order_lines[0].quantity == 3

    def test_add_line_to_non_pending_order(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)

        with pytest.raises(AcquisitionOrderNotPending):
            order.add_line(item_id='item1', unit_price=Decimal('19.99'), quantity=3)

    def test_remove_line(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.PENDING.value)
        line = AcquisitionOrderLine(id='line1', order_id='o1', item_id='item1', unit_price=Decimal('10.00'), quantity=5)
        order.order_lines.append(line)

        order.remove_line(order_line_id='line1')

        assert len(order.order_lines) == 0

    def test_remove_nonexistent_line(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.PENDING.value)

        with pytest.raises(DomainNotFound):
            order.remove_line(order_line_id='nonexistent')

    def test_remove_received_line(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.PENDING.value)
        line = AcquisitionOrderLine(
            id='line1',
            order_id='o1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            received_quantity=5,
            status=OrderLineStatus.RECEIVED.value,
        )
        order.order_lines.append(line)

        with pytest.raises(AcquisitionOrderLineAlreadyReceived):
            order.remove_line(order_line_id='line1')

    def test_submit_pending_order_with_lines(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.PENDING.value)
        line = AcquisitionOrderLine(id='line1', order_id='o1', item_id='item1', unit_price=Decimal('10.00'), quantity=5)
        order.order_lines.append(line)

        order.submit()

        assert order.status == OrderStatus.SUBMITTED.value

    def test_submit_pending_order_without_lines(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.PENDING.value)

        with pytest.raises(AcquisitionOrderHasNoLines):
            order.submit()

    def test_submit_non_pending_order(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)

        with pytest.raises(AcquisitionOrderNotPending):
            order.submit()

    def test_cancel_pending_order(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.PENDING.value)

        order.mark_as_cancelled()

        assert order.status == OrderStatus.CANCELLED.value

    def test_cancel_non_pending_order(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)

        with pytest.raises(AcquisitionOrderNotPending):
            order.mark_as_cancelled()

    def test_receive_line_full_quantity(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)
        line = AcquisitionOrderLine(
            id='line1',
            order_id='o1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            status=OrderLineStatus.PENDING.value,
        )
        order.order_lines.append(line)

        order.receive_line(order_line_id='line1', received_quantity=5)

        assert line.received_quantity == 5
        assert line.status == OrderLineStatus.RECEIVED.value
        assert order.status == OrderStatus.RECEIVED.value
        assert order.received_date is not None

    def test_receive_line_partial_quantity(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)
        line = AcquisitionOrderLine(
            id='line1',
            order_id='o1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            status=OrderLineStatus.PENDING.value,
        )
        order.order_lines.append(line)

        order.receive_line(order_line_id='line1', received_quantity=3)

        assert line.received_quantity == 3
        assert line.status == OrderLineStatus.PARTIALLY_RECEIVED.value
        # Order becomes RECEIVED when all lines have is_received() == True (including PARTIALLY_RECEIVED)
        assert order.status == OrderStatus.RECEIVED.value

    def test_receive_line_default_quantity(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)
        line = AcquisitionOrderLine(
            id='line1',
            order_id='o1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            status=OrderLineStatus.PENDING.value,
        )
        order.order_lines.append(line)

        order.receive_line(order_line_id='line1', received_quantity=None)

        assert line.received_quantity == 5

    def test_receive_line_not_submitted_order(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.PENDING.value)
        line = AcquisitionOrderLine(id='line1', order_id='o1', item_id='item1', unit_price=Decimal('10.00'), quantity=5)
        order.order_lines.append(line)

        with pytest.raises(AcquisitionOrderLineNotSubmitted):
            order.receive_line(order_line_id='line1', received_quantity=5)

    def test_receive_nonexistent_line(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)

        with pytest.raises(DomainNotFound):
            order.receive_line(order_line_id='nonexistent', received_quantity=5)

    def test_receive_already_received_line(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)
        line = AcquisitionOrderLine(
            id='line1',
            order_id='o1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            received_quantity=5,
            status=OrderLineStatus.RECEIVED.value,
        )
        order.order_lines.append(line)

        with pytest.raises(AcquisitionOrderLineAlreadyReceived):
            order.receive_line(order_line_id='line1', received_quantity=5)

    def test_receive_all_lines_marks_order_as_received(self, mock_event_bus: object) -> None:
        order = AcquisitionOrder(id='o1', vendor_id='v1', staff_id='s1', status=OrderStatus.SUBMITTED.value)
        line1 = AcquisitionOrderLine(
            id='line1',
            order_id='o1',
            item_id='item1',
            unit_price=Decimal('10.00'),
            quantity=5,
            status=OrderLineStatus.PENDING.value,
        )
        line2 = AcquisitionOrderLine(
            id='line2',
            order_id='o1',
            item_id='item2',
            unit_price=Decimal('15.00'),
            quantity=3,
            status=OrderLineStatus.PENDING.value,
        )
        order.order_lines.extend([line1, line2])

        order.receive_line(order_line_id='line1', received_quantity=5)
        assert order.status == OrderStatus.SUBMITTED.value

        order.receive_line(order_line_id='line2', received_quantity=3)
        assert order.status == OrderStatus.RECEIVED.value
        assert order.received_date == datetime.date.today()
