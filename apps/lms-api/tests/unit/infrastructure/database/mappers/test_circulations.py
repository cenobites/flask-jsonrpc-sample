"""Unit tests for circulations mappers - function-based with comprehensive coverage."""

import uuid
from datetime import date

from lms.domain.circulations.entities import Hold, Loan
from lms.infrastructure.database.models.circulations import HoldModel, LoanModel, HoldStatus
from lms.infrastructure.database.mappers.circulations import HoldMapper, LoanMapper


# LoanMapper Tests
def test_loan_mapper_to_entity_with_all_fields() -> None:
    model = LoanModel()
    model.id = uuid.uuid4()
    model.copy_id = uuid.uuid4()
    model.patron_id = uuid.uuid4()
    model.staff_out_id = uuid.uuid4()
    model.staff_in_id = uuid.uuid4()
    model.branch_id = uuid.uuid4()
    model.loan_date = date(2024, 1, 15)
    model.due_date = date(2024, 2, 15)
    model.return_date = date(2024, 2, 10)

    entity = LoanMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.copy_id == str(model.copy_id)
    assert entity.patron_id == str(model.patron_id)
    assert entity.staff_out_id == str(model.staff_out_id)
    assert entity.staff_in_id == str(model.staff_in_id)
    assert entity.branch_id == str(model.branch_id)
    assert entity.loan_date == date(2024, 1, 15)
    assert entity.due_date == date(2024, 2, 15)
    assert entity.return_date == date(2024, 2, 10)


def test_loan_mapper_to_entity_with_optional_fields_none() -> None:
    model = LoanModel()
    model.id = uuid.uuid4()
    model.copy_id = uuid.uuid4()
    model.patron_id = uuid.uuid4()
    model.staff_out_id = uuid.uuid4()
    model.staff_in_id = None
    model.branch_id = uuid.uuid4()
    model.loan_date = date(2024, 1, 15)
    model.due_date = date(2024, 2, 15)
    model.return_date = None

    entity = LoanMapper.to_entity(model)

    assert entity.staff_in_id is None
    assert entity.return_date is None


def test_loan_mapper_to_entity_without_id() -> None:
    model = LoanModel()
    model.id = None
    model.copy_id = uuid.uuid4()
    model.patron_id = uuid.uuid4()
    model.staff_out_id = uuid.uuid4()
    model.staff_in_id = None
    model.branch_id = uuid.uuid4()
    model.loan_date = date(2024, 1, 15)
    model.due_date = date(2024, 2, 15)
    model.return_date = None

    entity = LoanMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID


def test_loan_mapper_from_entity_with_all_fields() -> None:
    entity = Loan(
        id=str(uuid.uuid4()),
        copy_id=str(uuid.uuid4()),
        patron_id=str(uuid.uuid4()),
        staff_out_id=str(uuid.uuid4()),
        staff_in_id=str(uuid.uuid4()),
        branch_id=str(uuid.uuid4()),
        loan_date=date(2024, 1, 15),
        due_date=date(2024, 2, 15),
        return_date=date(2024, 2, 10),
    )

    model = LoanMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert str(model.copy_id) == entity.copy_id
    assert str(model.patron_id) == entity.patron_id
    assert str(model.staff_out_id) == entity.staff_out_id
    assert str(model.staff_in_id) == entity.staff_in_id
    assert str(model.branch_id) == entity.branch_id
    assert model.loan_date == date(2024, 1, 15)
    assert model.due_date == date(2024, 2, 15)
    assert model.return_date == date(2024, 2, 10)


def test_loan_mapper_from_entity_with_optional_fields_none() -> None:
    entity = Loan(
        id=str(uuid.uuid4()),
        copy_id=str(uuid.uuid4()),
        patron_id=str(uuid.uuid4()),
        staff_out_id=str(uuid.uuid4()),
        staff_in_id=None,
        branch_id=str(uuid.uuid4()),
        loan_date=date(2024, 1, 15),
        due_date=date(2024, 2, 15),
        return_date=None,
    )

    model = LoanMapper.from_entity(entity)

    assert model.staff_in_id is None
    assert model.return_date is None


def test_loan_mapper_from_entity_without_id() -> None:
    entity = Loan(
        id=None,
        copy_id=str(uuid.uuid4()),
        patron_id=str(uuid.uuid4()),
        staff_out_id=str(uuid.uuid4()),
        staff_in_id=None,
        branch_id=str(uuid.uuid4()),
        loan_date=date(2024, 1, 15),
        due_date=date(2024, 2, 15),
        return_date=None,
    )

    model = LoanMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity


# HoldMapper Tests
def test_hold_mapper_to_entity_with_all_fields() -> None:
    model = HoldModel()
    model.id = uuid.uuid4()
    model.item_id = uuid.uuid4()
    model.patron_id = uuid.uuid4()
    model.copy_id = uuid.uuid4()
    model.loan_id = uuid.uuid4()
    model.request_date = date(2024, 1, 15)
    model.expiry_date = date(2024, 1, 22)
    model.status = HoldStatus.PENDING

    entity = HoldMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.item_id == str(model.item_id)
    assert entity.patron_id == str(model.patron_id)
    assert entity.copy_id == str(model.copy_id)
    assert entity.loan_id == str(model.loan_id)
    assert entity.request_date == date(2024, 1, 15)
    assert entity.expiry_date == date(2024, 1, 22)
    assert entity.status == 'pending'


def test_hold_mapper_to_entity_with_optional_fields_none() -> None:
    model = HoldModel()
    model.id = uuid.uuid4()
    model.item_id = uuid.uuid4()
    model.patron_id = uuid.uuid4()
    model.copy_id = None
    model.loan_id = None
    model.request_date = date(2024, 1, 15)
    model.expiry_date = date(2024, 1, 22)
    model.status = HoldStatus.READY

    entity = HoldMapper.to_entity(model)

    assert entity.copy_id is None
    assert entity.loan_id is None
    assert entity.status == 'ready'


def test_hold_mapper_to_entity_without_id() -> None:
    model = HoldModel()
    model.id = None
    model.item_id = uuid.uuid4()
    model.patron_id = uuid.uuid4()
    model.copy_id = None
    model.loan_id = None
    model.request_date = date(2024, 1, 15)
    model.expiry_date = date(2024, 1, 22)
    model.status = HoldStatus.CANCELLED

    entity = HoldMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.status == 'cancelled'


def test_hold_mapper_from_entity_with_all_fields() -> None:
    entity = Hold(
        id=str(uuid.uuid4()),
        item_id=str(uuid.uuid4()),
        patron_id=str(uuid.uuid4()),
        copy_id=str(uuid.uuid4()),
        loan_id=str(uuid.uuid4()),
        request_date=date(2024, 1, 15),
        expiry_date=date(2024, 1, 22),
        status='pending',
    )

    model = HoldMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert str(model.item_id) == entity.item_id
    assert str(model.patron_id) == entity.patron_id
    assert str(model.copy_id) == entity.copy_id
    assert str(model.loan_id) == entity.loan_id
    assert model.request_date == date(2024, 1, 15)
    assert model.expiry_date == date(2024, 1, 22)
    assert model.status == HoldStatus.PENDING


def test_hold_mapper_from_entity_with_optional_fields_none() -> None:
    entity = Hold(
        id=str(uuid.uuid4()),
        item_id=str(uuid.uuid4()),
        patron_id=str(uuid.uuid4()),
        copy_id=None,
        loan_id=None,
        request_date=date(2024, 1, 15),
        expiry_date=date(2024, 1, 22),
        status='expired',
    )

    model = HoldMapper.from_entity(entity)

    assert model.copy_id is None
    assert model.loan_id is None
    assert model.status == HoldStatus.EXPIRED


def test_hold_mapper_from_entity_without_id() -> None:
    entity = Hold(
        id=None,
        item_id=str(uuid.uuid4()),
        patron_id=str(uuid.uuid4()),
        copy_id=None,
        loan_id=None,
        request_date=date(2024, 1, 15),
        expiry_date=date(2024, 1, 22),
        status='cancelled',
    )

    model = HoldMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.status == HoldStatus.CANCELLED
