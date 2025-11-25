"""Unit tests for patrons mappers - function-based with comprehensive coverage."""

import uuid
from decimal import Decimal
from datetime import date

from lms.domain.patrons.entities import Fine, Patron
from lms.infrastructure.database.models.patrons import FineModel, FineStatus, PatronModel, PatronStatus
from lms.infrastructure.database.mappers.patrons import FineMapper, PatronMapper


# PatronMapper Tests
def test_patron_mapper_to_entity_with_all_fields() -> None:
    model = PatronModel()
    model.id = uuid.uuid4()
    model.name = 'Alice Johnson'
    model.email = 'alice.johnson@example.com'
    model.branch_id = uuid.uuid4()
    model.member_since = date(2020, 1, 15)
    model.status = PatronStatus.ACTIVE

    entity = PatronMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.name == 'Alice Johnson'
    assert entity.email == 'alice.johnson@example.com'
    assert entity.branch_id == str(model.branch_id)
    assert entity.member_since == date(2020, 1, 15)
    assert entity.status == 'active'


def test_patron_mapper_to_entity_with_suspended_status() -> None:
    model = PatronModel()
    model.id = uuid.uuid4()
    model.name = 'Bob Smith'
    model.email = 'bob.smith@example.com'
    model.branch_id = uuid.uuid4()
    model.member_since = date(2019, 6, 1)
    model.status = PatronStatus.SUSPENDED

    entity = PatronMapper.to_entity(model)

    assert entity.status == 'suspended'


def test_patron_mapper_to_entity_without_id() -> None:
    model = PatronModel()
    model.id = None
    model.name = 'Charlie Brown'
    model.email = 'charlie.brown@example.com'
    model.branch_id = uuid.uuid4()
    model.member_since = date(2021, 3, 10)
    model.status = PatronStatus.ACTIVE

    entity = PatronMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID


def test_patron_mapper_from_entity_with_all_fields() -> None:
    entity = Patron(
        id=str(uuid.uuid4()),
        name='Alice Johnson',
        email='alice.johnson@example.com',
        branch_id=str(uuid.uuid4()),
        member_since=date(2020, 1, 15),
        status='active',
    )

    model = PatronMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.name == 'Alice Johnson'
    assert model.email == 'alice.johnson@example.com'
    assert str(model.branch_id) == entity.branch_id
    assert model.member_since == date(2020, 1, 15)
    assert model.status == PatronStatus.ACTIVE


def test_patron_mapper_from_entity_with_inactive_status() -> None:
    entity = Patron(
        id=str(uuid.uuid4()),
        name='David Williams',
        email='david.williams@example.com',
        branch_id=str(uuid.uuid4()),
        member_since=date(2018, 9, 20),
        status='archived',
    )

    model = PatronMapper.from_entity(entity)

    assert model.status == PatronStatus.ARCHIVED


def test_patron_mapper_from_entity_without_id() -> None:
    entity = Patron(
        id=None,
        name='Eve Davis',
        email='eve.davis@example.com',
        branch_id=str(uuid.uuid4()),
        member_since=date(2022, 2, 1),
        status='active',
    )

    model = PatronMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity


# FineMapper Tests
def test_fine_mapper_to_entity_with_all_fields() -> None:
    model = FineModel()
    model.id = uuid.uuid4()
    model.patron_id = uuid.uuid4()
    model.amount = Decimal('15.50')
    model.reason = 'Late return'
    model.issued_date = date(2024, 1, 20)
    model.paid_date = date(2024, 1, 25)
    model.status = FineStatus.PAID

    entity = FineMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.patron_id == str(model.patron_id)
    assert entity.loan_id == ''  # Mapper hardcodes this
    assert entity.amount == Decimal('15.50')
    assert entity.reason == 'Late return'
    assert entity.issued_date == date(2024, 1, 20)
    assert entity.paid_date == date(2024, 1, 25)
    assert entity.status == 'paid'


def test_fine_mapper_to_entity_with_optional_fields_none() -> None:
    model = FineModel()
    model.id = uuid.uuid4()
    model.patron_id = uuid.uuid4()
    model.amount = Decimal('10.00')
    model.reason = 'Damaged book'
    model.issued_date = date(2024, 2, 1)
    model.paid_date = None
    model.status = FineStatus.UNPAID

    entity = FineMapper.to_entity(model)

    assert entity.paid_date is None
    assert entity.status == 'unpaid'


def test_fine_mapper_to_entity_without_id() -> None:
    model = FineModel()
    model.id = None
    model.patron_id = uuid.uuid4()
    model.amount = Decimal('5.00')
    model.reason = 'Lost card'
    model.issued_date = date(2024, 2, 10)
    model.paid_date = None
    model.status = FineStatus.WAIVED

    entity = FineMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.status == 'waived'


def test_fine_mapper_from_entity_with_all_fields() -> None:
    entity = Fine(
        id=str(uuid.uuid4()),
        loan_id='',
        patron_id=str(uuid.uuid4()),
        amount=Decimal('15.50'),
        reason='Late return',
        issued_date=date(2024, 1, 20),
        paid_date=date(2024, 1, 25),
        status='paid',
    )

    model = FineMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert str(model.patron_id) == entity.patron_id
    assert model.amount == Decimal('15.50')
    assert model.reason == 'Late return'
    assert model.issued_date == date(2024, 1, 20)
    assert model.paid_date == date(2024, 1, 25)
    assert model.status == FineStatus.PAID


def test_fine_mapper_from_entity_with_optional_fields_none() -> None:
    entity = Fine(
        id=str(uuid.uuid4()),
        loan_id='',
        patron_id=str(uuid.uuid4()),
        amount=Decimal('10.00'),
        reason='Damaged book',
        issued_date=date(2024, 2, 1),
        paid_date=None,
        status='unpaid',
    )

    model = FineMapper.from_entity(entity)

    assert model.paid_date is None
    assert model.status == FineStatus.UNPAID


def test_fine_mapper_from_entity_without_id() -> None:
    entity = Fine(
        id=None,
        loan_id='',
        patron_id=str(uuid.uuid4()),
        amount=Decimal('5.00'),
        reason='Lost card',
        issued_date=date(2024, 2, 10),
        paid_date=None,
        status='waived',
    )

    model = FineMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.status == FineStatus.WAIVED
