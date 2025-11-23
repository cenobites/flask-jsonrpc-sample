from __future__ import annotations

from decimal import Decimal
from unittest.mock import Mock, MagicMock

import pytest

from lms.app.services.acquisitions import VendorService, AcquisitionOrderService
from lms.domain.acquisitions.entities import Vendor, AcquisitionOrder


@pytest.fixture
def mock_vendor_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_order_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_order_line_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def vendor_service(mock_vendor_repository: Mock) -> VendorService:
    return VendorService(vendor_repository=mock_vendor_repository)


@pytest.fixture
def order_service(mock_order_repository: Mock, mock_order_line_repository: Mock) -> AcquisitionOrderService:
    return AcquisitionOrderService(
        acquisition_order_repository=mock_order_repository, acquisition_order_line_repository=mock_order_line_repository
    )


def test_vendor_service_find_all_vendors(vendor_service: VendorService, mock_vendor_repository: Mock) -> None:
    mock_vendors = [Mock(spec=Vendor), Mock(spec=Vendor)]
    mock_vendor_repository.find_all.return_value = mock_vendors

    result = vendor_service.find_all_vendors()

    assert result == mock_vendors
    mock_vendor_repository.find_all.assert_called_once()


def test_vendor_service_get_vendor_success(vendor_service: VendorService, mock_vendor_repository: Mock) -> None:
    vendor = Mock(spec=Vendor, id='vendor-123')
    mock_vendor_repository.get_by_id.return_value = vendor

    result = vendor_service.get_vendor('vendor-123')

    assert result == vendor
    mock_vendor_repository.get_by_id.assert_called_once_with('vendor-123')


def test_vendor_service_get_vendor_not_found(vendor_service: VendorService, mock_vendor_repository: Mock) -> None:
    mock_vendor_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Vendor with id vendor-999 not found'):
        vendor_service.get_vendor('vendor-999')


def test_vendor_service_register_vendor(vendor_service: VendorService, mock_vendor_repository: Mock) -> None:
    vendor = Mock(spec=Vendor)
    mock_vendor_repository.save.return_value = vendor

    result = vendor_service.register_vendor(
        name='Test Vendor', staff_id='staff-123', address='123 Main St', email='test@vendor.com', phone='555-1234'
    )

    assert result == vendor
    mock_vendor_repository.save.assert_called_once()


def test_vendor_service_register_vendor_minimal(vendor_service: VendorService, mock_vendor_repository: Mock) -> None:
    vendor = Mock(spec=Vendor)
    mock_vendor_repository.save.return_value = vendor

    result = vendor_service.register_vendor(name='Test Vendor', staff_id='staff-123')

    assert result == vendor
    mock_vendor_repository.save.assert_called_once()


def test_vendor_service_update_vendor(vendor_service: VendorService, mock_vendor_repository: Mock) -> None:
    vendor = Mock(spec=Vendor, id='vendor-123', name='Old Name', address='Old Address')
    mock_vendor_repository.get_by_id.return_value = vendor
    mock_vendor_repository.save.return_value = vendor

    result = vendor_service.update_vendor('vendor-123', name='New Name', address='New Address')

    assert result == vendor
    assert vendor.name == 'New Name'
    assert vendor.address == 'New Address'
    mock_vendor_repository.save.assert_called_once()


def test_vendor_service_update_vendor_partial(vendor_service: VendorService, mock_vendor_repository: Mock) -> None:
    vendor = Mock(spec=Vendor)
    vendor.id = 'vendor-123'
    vendor.name = 'Test'
    vendor.email = 'old@test.com'
    mock_vendor_repository.get_by_id.return_value = vendor
    mock_vendor_repository.save.return_value = vendor

    result = vendor_service.update_vendor('vendor-123', email='new@test.com')

    assert result == vendor
    assert vendor.email == 'new@test.com'


def test_order_service_find_all_orders(order_service: AcquisitionOrderService, mock_order_repository: Mock) -> None:
    mock_orders = [Mock(spec=AcquisitionOrder), Mock(spec=AcquisitionOrder)]
    mock_order_repository.find_all.return_value = mock_orders

    result = order_service.find_all_orders()

    assert result == mock_orders
    mock_order_repository.find_all.assert_called_once()


def test_order_service_get_order_success(order_service: AcquisitionOrderService, mock_order_repository: Mock) -> None:
    order = Mock(spec=AcquisitionOrder, id='order-123')
    mock_order_repository.get_by_id.return_value = order

    result = order_service.get_order('order-123')

    assert result == order
    mock_order_repository.get_by_id.assert_called_once_with('order-123')


def test_order_service_get_order_not_found(order_service: AcquisitionOrderService, mock_order_repository: Mock) -> None:
    mock_order_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Acquisition order with id order-999 not found'):
        order_service.get_order('order-999')


def test_order_service_create_order(order_service: AcquisitionOrderService, mock_order_repository: Mock) -> None:
    order = Mock(spec=AcquisitionOrder)
    mock_order_repository.save.return_value = order

    result = order_service.create_order(vendor_id='vendor-123', staff_id='staff-456')

    assert result == order
    mock_order_repository.save.assert_called_once()


def test_order_service_add_line_to_order(order_service: AcquisitionOrderService, mock_order_repository: Mock) -> None:
    order = Mock(spec=AcquisitionOrder, id='order-123')
    mock_order_repository.get_by_id.return_value = order
    mock_order_repository.save.return_value = order

    result = order_service.add_line_to_order('order-123', 'item-456', 5, Decimal('29.99'))

    assert result == order
    order.add_line.assert_called_once_with(item_id='item-456', unit_price=Decimal('29.99'), quantity=5)
    mock_order_repository.save.assert_called_once()


def test_order_service_add_line_order_not_found(
    order_service: AcquisitionOrderService, mock_order_repository: Mock
) -> None:
    mock_order_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Acquisition order with id order-999 not found'):
        order_service.add_line_to_order('order-999', 'item-1', 1, Decimal('10.00'))


def test_order_service_remove_line_from_order(
    order_service: AcquisitionOrderService, mock_order_repository: Mock
) -> None:
    order = Mock(spec=AcquisitionOrder, id='order-123')
    mock_order_repository.get_by_id.return_value = order
    mock_order_repository.save.return_value = order

    result = order_service.remove_line_from_order('order-123', 'line-456')

    assert result == order
    order.remove_line.assert_called_once_with(order_line_id='line-456')


def test_order_service_receive_line_from_order(
    order_service: AcquisitionOrderService, mock_order_repository: Mock
) -> None:
    order = Mock(spec=AcquisitionOrder, id='order-123')
    mock_order_repository.get_by_id.return_value = order
    mock_order_repository.save.return_value = order

    result = order_service.receive_line_from_order('order-123', 'line-456', received_quantity=3)

    assert result == order
    order.receive_line.assert_called_once_with(order_line_id='line-456', received_quantity=3)


def test_order_service_receive_line_default_quantity(
    order_service: AcquisitionOrderService, mock_order_repository: Mock
) -> None:
    order = Mock(spec=AcquisitionOrder, id='order-123')
    mock_order_repository.get_by_id.return_value = order
    mock_order_repository.save.return_value = order

    result = order_service.receive_line_from_order('order-123', 'line-456')

    assert result == order
    order.receive_line.assert_called_once_with(order_line_id='line-456', received_quantity=None)


def test_order_service_submit_order(order_service: AcquisitionOrderService, mock_order_repository: Mock) -> None:
    order = Mock(spec=AcquisitionOrder, id='order-123')
    mock_order_repository.get_by_id.return_value = order
    mock_order_repository.save.return_value = order

    result = order_service.submit_order('order-123')

    assert result == order
    order.submit.assert_called_once()


def test_order_service_cancel_order(order_service: AcquisitionOrderService, mock_order_repository: Mock) -> None:
    order = Mock(spec=AcquisitionOrder, id='order-123')
    mock_order_repository.get_by_id.return_value = order
    mock_order_repository.save.return_value = order

    result = order_service.cancel_order('order-123')

    assert result == order
    order.mark_as_cancelled.assert_called_once()
