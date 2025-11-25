from __future__ import annotations

import pytest
from pydantic import ValidationError

from lms.app.schemas.organizations import StaffCreate, StaffUpdate, BranchCreate, BranchUpdate


def test_branch_create_minimal_fields() -> None:
    branch = BranchCreate(name='Downtown Library')

    assert branch.name == 'Downtown Library'
    assert branch.manager_id is None
    assert branch.address is None
    assert branch.phone is None
    assert branch.email is None


def test_branch_create_all_fields() -> None:
    branch = BranchCreate(
        name='Central Library',
        manager_id='mgr-123',
        address='123 Main St',
        phone='555-1234',
        email='central@library.com',
    )

    assert branch.name == 'Central Library'
    assert branch.manager_id == 'mgr-123'
    assert branch.address == '123 Main St'
    assert branch.phone == '555-1234'
    assert branch.email == 'central@library.com'


def test_branch_create_requires_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        BranchCreate()  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('name',) for error in errors)


def test_branch_create_name_min_length() -> None:
    with pytest.raises(ValidationError) as exc_info:
        BranchCreate(name='')

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_branch_create_name_max_length() -> None:
    long_name = 'A' * 101

    with pytest.raises(ValidationError) as exc_info:
        BranchCreate(name=long_name)

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_branch_create_address_max_length() -> None:
    long_address = 'A' * 256

    with pytest.raises(ValidationError) as exc_info:
        BranchCreate(name='Test Branch', address=long_address)

    errors = exc_info.value.errors()
    assert any('address' in str(error['loc']) for error in errors)


def test_branch_create_phone_max_length() -> None:
    long_phone = '1' * 21

    with pytest.raises(ValidationError) as exc_info:
        BranchCreate(name='Test Branch', phone=long_phone)

    errors = exc_info.value.errors()
    assert any('phone' in str(error['loc']) for error in errors)


def test_branch_create_email_max_length() -> None:
    long_email = 'a' * 95 + '@test.com'

    with pytest.raises(ValidationError) as exc_info:
        BranchCreate(name='Test Branch', email=long_email)

    errors = exc_info.value.errors()
    assert any('email' in str(error['loc']) for error in errors)


def test_branch_create_strips_whitespace() -> None:
    branch = BranchCreate(name='  Test Branch  ')

    assert branch.name == 'Test Branch'


def test_branch_update_requires_branch_id_and_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        BranchUpdate(branch_id='branch-123')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('name',) for error in errors)


def test_branch_update_all_fields() -> None:
    branch = BranchUpdate(branch_id='branch-123', name='Updated Branch', address='456 New St', phone='555-9999')

    assert branch.branch_id == 'branch-123'
    assert branch.name == 'Updated Branch'
    assert branch.address == '456 New St'
    assert branch.phone == '555-9999'


def test_branch_update_minimal_fields() -> None:
    branch = BranchUpdate(branch_id='branch-123', name='Test Branch')

    assert branch.branch_id == 'branch-123'
    assert branch.name == 'Test Branch'
    assert branch.address is None
    assert branch.phone is None


def test_branch_update_name_validation() -> None:
    with pytest.raises(ValidationError):
        BranchUpdate(branch_id='branch-123', name='')


def test_staff_create_all_fields() -> None:
    staff = StaffCreate(name='John Doe', email='john.doe@library.com', role='librarian')

    assert staff.name == 'John Doe'
    assert staff.email == 'john.doe@library.com'
    assert staff.role == 'librarian'


def test_staff_create_requires_all_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        StaffCreate(name='John Doe', email='john@library.com')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('role',) for error in errors)


def test_staff_create_name_min_length() -> None:
    with pytest.raises(ValidationError) as exc_info:
        StaffCreate(name='', email='test@library.com', role='librarian')

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_staff_create_name_max_length() -> None:
    long_name = 'A' * 101

    with pytest.raises(ValidationError) as exc_info:
        StaffCreate(name=long_name, email='test@library.com', role='librarian')

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_staff_create_email_validation() -> None:
    with pytest.raises(ValidationError) as exc_info:
        StaffCreate(name='John Doe', email='invalid-email', role='librarian')

    errors = exc_info.value.errors()
    assert any('email' in str(error['loc']) for error in errors)


def test_staff_create_different_roles() -> None:
    roles = ['librarian', 'technician', 'manager', 'assistant']

    for role in roles:
        staff = StaffCreate(name='Test Staff', email='test@library.com', role=role)
        assert staff.role == role


def test_staff_create_strips_whitespace() -> None:
    staff = StaffCreate(name='  John Doe  ', email='john@library.com', role='librarian')

    assert staff.name == 'John Doe'


def test_staff_update_requires_staff_id_and_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        StaffUpdate(staff_id='staff-123')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('name',) for error in errors)


def test_staff_update_all_fields() -> None:
    staff = StaffUpdate(staff_id='staff-123', name='Updated Name')

    assert staff.staff_id == 'staff-123'
    assert staff.name == 'Updated Name'


def test_staff_update_name_validation() -> None:
    with pytest.raises(ValidationError):
        StaffUpdate(staff_id='staff-123', name='')

    long_name = 'A' * 101
    with pytest.raises(ValidationError):
        StaffUpdate(staff_id='staff-123', name=long_name)


def test_branch_create_serialization() -> None:
    branch = BranchCreate(name='Test Branch', manager_id='mgr-1')
    data = branch.model_dump()

    assert data['name'] == 'Test Branch'
    assert data['manager_id'] == 'mgr-1'


def test_staff_create_serialization() -> None:
    staff = StaffCreate(name='John Doe', email='john@test.com', role='librarian')
    data = staff.model_dump()

    assert data['name'] == 'John Doe'
    assert data['email'] == 'john@test.com'
    assert data['role'] == 'librarian'
