from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from lms.app.schemas.acquisitions import OrderCreate, OrderLineAdd, VendorUpdate, VendorRegister, OrderLineCreate


def test_order_line_create_valid() -> None:
    order_line = OrderLineCreate(item_id='item-123', quantity=5, unit_price=Decimal('29.99'))

    assert order_line.item_id == 'item-123'
    assert order_line.quantity == 5
    assert order_line.unit_price == Decimal('29.99')


def test_order_line_create_requires_all_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        OrderLineCreate(item_id='item-123', quantity=5)  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('unit_price',) for error in errors)


def test_order_line_create_with_zero_quantity() -> None:
    order_line = OrderLineCreate(item_id='item-123', quantity=0, unit_price=Decimal('10.00'))

    assert order_line.quantity == 0


def test_order_line_create_with_decimal_price() -> None:
    test_cases = [Decimal('0.01'), Decimal('99.99'), Decimal('1000.00'), Decimal('0.00')]

    for price in test_cases:
        order_line = OrderLineCreate(item_id='item-123', quantity=1, unit_price=price)
        assert order_line.unit_price == price


def test_order_create_with_order_lines() -> None:
    lines = [
        OrderLineCreate(item_id='item-1', quantity=2, unit_price=Decimal('15.00')),
        OrderLineCreate(item_id='item-2', quantity=1, unit_price=Decimal('25.00')),
    ]

    order = OrderCreate(vendor_id='vendor-123', staff_id='staff-456', order_lines=lines)

    assert order.vendor_id == 'vendor-123'
    assert order.staff_id == 'staff-456'
    assert len(order.order_lines) == 2
    assert order.order_lines[0].item_id == 'item-1'
    assert order.order_lines[1].item_id == 'item-2'


def test_order_create_without_order_lines() -> None:
    order = OrderCreate(vendor_id='vendor-123', staff_id='staff-456')

    assert order.vendor_id == 'vendor-123'
    assert order.staff_id == 'staff-456'
    assert order.order_lines == []


def test_order_create_requires_vendor_and_staff() -> None:
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(vendor_id='vendor-123')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('staff_id',) for error in errors)


def test_order_line_add_valid() -> None:
    order_line_add = OrderLineAdd(order_id='order-789', item_id='item-123', quantity=3, unit_price=Decimal('19.99'))

    assert order_line_add.order_id == 'order-789'
    assert order_line_add.item_id == 'item-123'
    assert order_line_add.quantity == 3
    assert order_line_add.unit_price == Decimal('19.99')


def test_order_line_add_requires_all_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        OrderLineAdd(order_id='order-789', item_id='item-123', quantity=1)  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('unit_price',) for error in errors)


def test_vendor_register_with_all_fields() -> None:
    vendor = VendorRegister(
        name='ABC Suppliers', staff_id='staff-123', email='contact@abc.com', phone='555-1234', address='123 Main St'
    )

    assert vendor.name == 'ABC Suppliers'
    assert vendor.staff_id == 'staff-123'
    assert vendor.email == 'contact@abc.com'
    assert vendor.phone == '555-1234'
    assert vendor.address == '123 Main St'


def test_vendor_register_without_optional_fields() -> None:
    vendor = VendorRegister(name='ABC Suppliers', staff_id='staff-123')

    assert vendor.name == 'ABC Suppliers'
    assert vendor.staff_id == 'staff-123'
    assert vendor.email is None
    assert vendor.phone is None
    assert vendor.address is None


def test_vendor_register_name_max_length() -> None:
    long_name = 'A' * 256

    with pytest.raises(ValidationError) as exc_info:
        VendorRegister(name=long_name, staff_id='staff-123')

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_vendor_register_email_max_length() -> None:
    long_email = 'a' * 250 + '@test.com'

    with pytest.raises(ValidationError) as exc_info:
        VendorRegister(name='Test Vendor', staff_id='staff-123', email=long_email)

    errors = exc_info.value.errors()
    assert any('email' in str(error['loc']) for error in errors)


def test_vendor_register_phone_max_length() -> None:
    long_phone = '1' * 21

    with pytest.raises(ValidationError) as exc_info:
        VendorRegister(name='Test Vendor', staff_id='staff-123', phone=long_phone)

    errors = exc_info.value.errors()
    assert any('phone' in str(error['loc']) for error in errors)


def test_vendor_update_with_all_fields() -> None:
    vendor = VendorUpdate(
        id='vendor-123', name='Updated Vendor', email='updated@vendor.com', phone='555-9999', address='456 New St'
    )

    assert vendor.id == 'vendor-123'
    assert vendor.name == 'Updated Vendor'
    assert vendor.email == 'updated@vendor.com'
    assert vendor.phone == '555-9999'
    assert vendor.address == '456 New St'


def test_vendor_update_requires_id_and_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        VendorUpdate(id='vendor-123')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('name',) for error in errors)


def test_vendor_update_with_none_optional_fields() -> None:
    vendor = VendorUpdate(id='vendor-123', name='Test Vendor', email=None, phone=None, address=None)

    assert vendor.id == 'vendor-123'
    assert vendor.name == 'Test Vendor'
    assert vendor.email is None
    assert vendor.phone is None
    assert vendor.address is None


def test_order_create_serialization() -> None:
    order = OrderCreate(vendor_id='v-1', staff_id='s-1', order_lines=[])
    data = order.model_dump()

    assert data == {'vendor_id': 'v-1', 'staff_id': 's-1', 'order_lines': []}


def test_vendor_register_strips_whitespace() -> None:
    vendor = VendorRegister(name='  Test Vendor  ', staff_id='  staff-123  ')

    assert vendor.name == 'Test Vendor'
    assert vendor.staff_id == 'staff-123'
