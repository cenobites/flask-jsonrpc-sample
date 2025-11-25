"""Unit tests for organizations mappers - function-based with comprehensive coverage."""

import uuid
from datetime import date

from lms.domain.organizations.entities import Staff, Branch
from lms.infrastructure.database.models.organizations import (
    StaffRole,
    StaffModel,
    BranchModel,
    StaffStatus,
    BranchStatus,
)
from lms.infrastructure.database.mappers.organizations import StaffMapper, BranchMapper


# BranchMapper Tests
def test_branch_mapper_to_entity_with_all_fields() -> None:
    model = BranchModel()
    model.id = uuid.uuid4()
    model.name = 'Main Branch'
    model.address = '123 Library St'
    model.phone = '555-0100'
    model.email = 'main@library.org'
    model.manager_id = uuid.uuid4()
    model.status = BranchStatus.ACTIVE

    entity = BranchMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.name == 'Main Branch'
    assert entity.address == '123 Library St'
    assert entity.phone == '555-0100'
    assert entity.email == 'main@library.org'
    assert entity.manager_id == str(model.manager_id)
    assert entity.status == 'active'


def test_branch_mapper_to_entity_with_optional_fields_none() -> None:
    model = BranchModel()
    model.id = uuid.uuid4()
    model.name = 'Branch Library'
    model.address = '456 Book Ave'
    model.phone = '555-0200'
    model.email = 'branch@library.org'
    model.manager_id = None
    model.status = BranchStatus.CLOSED

    entity = BranchMapper.to_entity(model)

    assert entity.manager_id is None
    assert entity.status == 'closed'


def test_branch_mapper_to_entity_without_id() -> None:
    model = BranchModel()
    model.id = None
    model.name = 'New Branch'
    model.address = '789 Reading Rd'
    model.phone = '555-0300'
    model.email = 'new@library.org'
    model.manager_id = None
    model.status = BranchStatus.ACTIVE

    entity = BranchMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID


def test_branch_mapper_from_entity_with_all_fields() -> None:
    entity = Branch(
        id=str(uuid.uuid4()),
        name='Main Branch',
        address='123 Library St',
        phone='555-0100',
        email='main@library.org',
        manager_id=str(uuid.uuid4()),
        status='active',
    )

    model = BranchMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.name == 'Main Branch'
    assert model.address == '123 Library St'
    assert model.phone == '555-0100'
    assert model.email == 'main@library.org'
    assert str(model.manager_id) == entity.manager_id
    assert model.status == BranchStatus.ACTIVE


def test_branch_mapper_from_entity_with_optional_fields_none() -> None:
    entity = Branch(
        id=str(uuid.uuid4()),
        name='Branch Library',
        address='456 Book Ave',
        phone='555-0200',
        email='branch@library.org',
        manager_id=None,
        status='closed',
    )

    model = BranchMapper.from_entity(entity)

    assert model.manager_id is None
    assert model.status == BranchStatus.CLOSED


def test_branch_mapper_from_entity_without_id() -> None:
    entity = Branch(
        id=None,
        name='New Branch',
        address='789 Reading Rd',
        phone='555-0300',
        email='new@library.org',
        manager_id=None,
        status='active',
    )

    model = BranchMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity


# StaffMapper Tests
def test_staff_mapper_to_entity_with_all_fields() -> None:
    model = StaffModel()
    model.id = uuid.uuid4()
    model.name = 'John Doe'
    model.email = 'john.doe@library.org'
    model.role = StaffRole.LIBRARIAN
    model.status = StaffStatus.ACTIVE
    model.branch_id = uuid.uuid4()
    model.hire_date = date(2024, 1, 15)

    entity = StaffMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.name == 'John Doe'
    assert entity.email == 'john.doe@library.org'
    assert entity.role == 'librarian'
    assert entity.status == 'active'
    assert entity.branch_id == str(model.branch_id)


def test_staff_mapper_to_entity_with_optional_fields_none() -> None:
    model = StaffModel()
    model.id = uuid.uuid4()
    model.name = 'Jane Smith'
    model.email = 'jane.smith@library.org'
    model.role = StaffRole.MANAGER
    model.status = StaffStatus.INACTIVE
    model.branch_id = None
    model.hire_date = date(2023, 6, 1)

    entity = StaffMapper.to_entity(model)

    assert entity.branch_id is None
    assert entity.role == 'manager'
    assert entity.status == 'inactive'


def test_staff_mapper_to_entity_without_id() -> None:
    model = StaffModel()
    model.id = None
    model.name = 'Bob Wilson'
    model.email = 'bob.wilson@library.org'
    model.role = StaffRole.TECHNICIAN
    model.status = StaffStatus.ACTIVE
    model.branch_id = uuid.uuid4()
    model.hire_date = date(2024, 2, 1)

    entity = StaffMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.role == 'technician'


def test_staff_mapper_from_entity_with_all_fields() -> None:
    entity = Staff(
        id=str(uuid.uuid4()),
        name='John Doe',
        email='john.doe@library.org',
        role='librarian',
        status='active',
        branch_id=str(uuid.uuid4()),
        hire_date=date(2024, 1, 15),
    )

    model = StaffMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.name == 'John Doe'
    assert model.email == 'john.doe@library.org'
    assert model.role == StaffRole.LIBRARIAN
    assert model.status == StaffStatus.ACTIVE
    assert str(model.branch_id) == entity.branch_id


def test_staff_mapper_from_entity_with_optional_fields_none() -> None:
    entity = Staff(
        id=str(uuid.uuid4()),
        name='Jane Smith',
        email='jane.smith@library.org',
        role='manager',
        status='inactive',
        branch_id=None,
        hire_date=date(2023, 6, 1),
    )

    model = StaffMapper.from_entity(entity)

    assert model.branch_id is None
    assert model.role == StaffRole.MANAGER
    assert model.status == StaffStatus.INACTIVE


def test_staff_mapper_from_entity_without_id() -> None:
    entity = Staff(
        id=None,
        name='Bob Wilson',
        email='bob.wilson@library.org',
        role='technician',
        status='active',
        branch_id=str(uuid.uuid4()),
        hire_date=date(2024, 2, 1),
    )

    model = StaffMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.role == StaffRole.TECHNICIAN
