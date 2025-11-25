"""Unit tests for acquisitions mappers - function-based with comprehensive coverage."""

import uuid
from datetime import date

from lms.domain.acquisitions.entities import Vendor, AcquisitionOrder, AcquisitionOrderLine
from lms.infrastructure.database.models.acquisitions import (
    OrderStatus,
    VendorModel,
    OrderLineStatus,
    AcquisitionOrderModel,
    AcquisitionOrderLineModel,
)
from lms.infrastructure.database.mappers.acquisitions import (
    VendorMapper,
    AcquisitionOrderMapper,
    AcquisitionOrderLineMapper,
)


# VendorMapper Tests
def test_vendor_mapper_to_entity_with_id() -> None:
    model = VendorModel()
    model.id = uuid.uuid4()
    model.name = 'Test Vendor'
    model.address = '123 Test St'
    model.email = 'vendor@test.com'
    model.phone = '555-0100'

    entity = VendorMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.name == 'Test Vendor'
    assert entity.address == '123 Test St'
    assert entity.email == 'vendor@test.com'
    assert entity.phone == '555-0100'


def test_vendor_mapper_to_entity_without_id() -> None:
    model = VendorModel()
    model.id = None
    model.name = 'Test Vendor'
    model.address = '123 Test St'
    model.email = 'vendor@test.com'
    model.phone = '555-0100'

    entity = VendorMapper.to_entity(model)

    # Entity auto-generates ID in __post_init__ when None is passed
    assert entity.id is not None
    assert entity.name == 'Test Vendor'


def test_vendor_mapper_from_entity_with_id() -> None:
    entity = Vendor(
        id=str(uuid.uuid4()), name='Test Vendor', address='123 Test St', email='vendor@test.com', phone='555-0100'
    )

    model = VendorMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.name == 'Test Vendor'
    assert model.address == '123 Test St'
    assert model.email == 'vendor@test.com'
    assert model.phone == '555-0100'


def test_vendor_mapper_from_entity_without_id() -> None:
    entity = Vendor(id=None, name='Test Vendor', address='123 Test St', email='vendor@test.com', phone='555-0100')

    model = VendorMapper.from_entity(entity)

    # Model gets auto-generated ID from entity
    assert model.id is not None
    assert model.name == 'Test Vendor'


# AcquisitionOrderLineMapper Tests
def test_acquisition_order_line_mapper_to_entity_with_id() -> None:
    model = AcquisitionOrderLineModel()
    model.id = uuid.uuid4()
    model.order_id = uuid.uuid4()
    model.item_id = uuid.uuid4()
    model.unit_price = 29.99
    model.quantity = 5
    model.status = OrderLineStatus.PENDING
    model.received_quantity = 0

    entity = AcquisitionOrderLineMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.order_id == str(model.order_id)
    assert entity.item_id == str(model.item_id)
    assert entity.unit_price == 29.99
    assert entity.quantity == 5
    assert entity.status == 'pending'
    assert entity.received_quantity == 0


def test_acquisition_order_line_mapper_to_entity_without_id() -> None:
    model = AcquisitionOrderLineModel()
    model.id = None
    model.order_id = uuid.uuid4()
    model.item_id = uuid.uuid4()
    model.unit_price = 29.99
    model.quantity = 5
    model.status = OrderLineStatus.RECEIVED
    model.received_quantity = 5

    entity = AcquisitionOrderLineMapper.to_entity(model)

    # Entity auto-generates ID in __post_init__
    assert entity.id is not None
    assert entity.status == 'received'
    assert entity.received_quantity == 5


def test_acquisition_order_line_mapper_from_entity_with_id() -> None:
    entity = AcquisitionOrderLine(
        id=str(uuid.uuid4()),
        order_id=str(uuid.uuid4()),
        item_id=str(uuid.uuid4()),
        unit_price=29.99,
        quantity=5,
        status='pending',
        received_quantity=0,
    )

    model = AcquisitionOrderLineMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert str(model.order_id) == entity.order_id
    assert str(model.item_id) == entity.item_id
    assert model.unit_price == 29.99
    assert model.quantity == 5
    assert model.status == OrderLineStatus.PENDING
    assert model.received_quantity == 0


def test_acquisition_order_line_mapper_from_entity_without_id() -> None:
    entity = AcquisitionOrderLine(
        id=None,
        order_id=str(uuid.uuid4()),
        item_id=str(uuid.uuid4()),
        unit_price=29.99,
        quantity=5,
        status='pending',
        received_quantity=0,
    )

    model = AcquisitionOrderLineMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.status == OrderLineStatus.PENDING


# AcquisitionOrderMapper Tests
def test_acquisition_order_mapper_to_entity_with_id() -> None:
    order_line_model = AcquisitionOrderLineModel()
    order_line_model.id = uuid.uuid4()
    order_line_model.order_id = uuid.uuid4()
    order_line_model.item_id = uuid.uuid4()
    order_line_model.unit_price = 29.99
    order_line_model.quantity = 5
    order_line_model.status = OrderLineStatus.PENDING
    order_line_model.received_quantity = 0

    model = AcquisitionOrderModel()
    model.id = uuid.uuid4()
    model.vendor_id = uuid.uuid4()
    model.staff_id = uuid.uuid4()
    model.order_date = date(2024, 1, 15)
    model.received_date = None
    model.status = OrderStatus.PENDING
    model.order_lines = [order_line_model]

    entity = AcquisitionOrderMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.vendor_id == str(model.vendor_id)
    assert entity.staff_id == str(model.staff_id)
    assert entity.order_date == date(2024, 1, 15)
    assert entity.received_date is None
    assert entity.status == 'pending'
    assert len(entity.order_lines) == 1
    assert entity.order_lines[0].id == str(order_line_model.id)


def test_acquisition_order_mapper_to_entity_without_id() -> None:
    model = AcquisitionOrderModel()
    model.id = None
    model.vendor_id = uuid.uuid4()
    model.staff_id = uuid.uuid4()
    model.order_date = date(2024, 1, 15)
    model.received_date = date(2024, 1, 20)
    model.status = OrderStatus.RECEIVED
    model.order_lines = []

    entity = AcquisitionOrderMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.received_date == date(2024, 1, 20)
    assert entity.status == 'received'
    assert len(entity.order_lines) == 0


def test_acquisition_order_mapper_from_entity_with_id() -> None:
    order_line = AcquisitionOrderLine(
        id=str(uuid.uuid4()),
        order_id=str(uuid.uuid4()),
        item_id=str(uuid.uuid4()),
        unit_price=29.99,
        quantity=5,
        status='pending',
        received_quantity=0,
    )

    entity = AcquisitionOrder(
        id=str(uuid.uuid4()),
        vendor_id=str(uuid.uuid4()),
        staff_id=str(uuid.uuid4()),
        order_date=date(2024, 1, 15),
        received_date=None,
        status='pending',
        order_lines=[order_line],
    )

    model = AcquisitionOrderMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert str(model.vendor_id) == entity.vendor_id
    assert str(model.staff_id) == entity.staff_id
    assert model.order_date == date(2024, 1, 15)
    assert model.received_date is None
    assert model.status == OrderStatus.PENDING
    assert len(model.order_lines) == 1
    assert str(model.order_lines[0].id) == order_line.id


def test_acquisition_order_mapper_from_entity_without_id() -> None:
    entity = AcquisitionOrder(
        id=None,
        vendor_id=str(uuid.uuid4()),
        staff_id=str(uuid.uuid4()),
        order_date=date(2024, 1, 15),
        received_date=date(2024, 1, 20),
        status='cancelled',
        order_lines=[],
    )

    model = AcquisitionOrderMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.received_date == date(2024, 1, 20)
    assert model.status == OrderStatus.CANCELLED
    assert len(model.order_lines) == 0


def test_acquisition_order_mapper_with_multiple_order_lines() -> None:
    line1 = AcquisitionOrderLine(
        id=str(uuid.uuid4()),
        order_id=str(uuid.uuid4()),
        item_id=str(uuid.uuid4()),
        unit_price=29.99,
        quantity=5,
        status='pending',
        received_quantity=0,
    )

    line2 = AcquisitionOrderLine(
        id=str(uuid.uuid4()),
        order_id=str(uuid.uuid4()),
        item_id=str(uuid.uuid4()),
        unit_price=19.99,
        quantity=3,
        status='received',
        received_quantity=3,
    )

    entity = AcquisitionOrder(
        id=str(uuid.uuid4()),
        vendor_id=str(uuid.uuid4()),
        staff_id=str(uuid.uuid4()),
        order_date=date(2024, 1, 15),
        received_date=None,
        status='pending',
        order_lines=[line1, line2],
    )

    model = AcquisitionOrderMapper.from_entity(entity)

    assert len(model.order_lines) == 2
    assert model.order_lines[0].unit_price == 29.99
    assert model.order_lines[1].unit_price == 19.99
