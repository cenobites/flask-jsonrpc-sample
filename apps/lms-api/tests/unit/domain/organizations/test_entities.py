from __future__ import annotations

import datetime
from unittest.mock import Mock, patch
from collections.abc import Iterator

import pytest

from lms.domain.organizations.entities import Staff, Branch
from lms.domain.organizations.exceptions import (
    StaffNotActive,
    StaffNotManager,
    BranchAlreadyClosed,
    BranchNameAlreadyExists,
    StaffEmailAlreadyExists,
)
from lms.infrastructure.database.models.organizations import StaffRole, StaffStatus, BranchStatus


@pytest.fixture
def mock_event_bus() -> Iterator:
    with patch('lms.domain.organizations.entities.event_bus') as mock_bus:
        yield mock_bus


@pytest.fixture
def mock_branch_uniqueness_service() -> Iterator:
    service = Mock()
    service.is_name_unique.return_value = True
    return service


@pytest.fixture
def mock_staff_uniqueness_service() -> Iterator:
    service = Mock()
    service.is_email_unique.return_value = True
    return service


@pytest.fixture
def mock_branch_assignment_service() -> Iterator:
    service = Mock()
    service.can_assign_manager.return_value = True
    return service


class TestBranch:
    def test_create_branch_minimal(self, mock_event_bus: object, mock_branch_uniqueness_service: object) -> None:
        branch = Branch.create(name='Main Library', branch_uniqueness_service=mock_branch_uniqueness_service)

        assert branch.name == 'Main Library'
        assert branch.address is None
        assert branch.phone is None
        assert branch.email is None
        assert branch.status == BranchStatus.OPEN.value
        assert branch.manager_id is None
        mock_event_bus.add_event.assert_called_once()

    def test_create_branch_full(self, mock_event_bus: object, mock_branch_uniqueness_service: object) -> None:
        branch = Branch.create(
            name='Downtown Branch',
            address='123 Main St',
            phone='555-0100',
            email='downtown@library.org',
            branch_uniqueness_service=mock_branch_uniqueness_service,
        )

        assert branch.name == 'Downtown Branch'
        assert branch.address == '123 Main St'
        assert branch.phone == '555-0100'
        assert branch.email == 'downtown@library.org'

    def test_create_branch_duplicate_name(self, mock_event_bus: object, mock_branch_uniqueness_service: object) -> None:
        mock_branch_uniqueness_service.is_name_unique.return_value = False

        with pytest.raises(BranchNameAlreadyExists):
            Branch.create(name='Duplicate', branch_uniqueness_service=mock_branch_uniqueness_service)

    def test_change_name(self, mock_event_bus: object, mock_branch_uniqueness_service: object) -> None:
        branch = Branch(id='b1', name='Old Name', status=BranchStatus.OPEN.value)

        branch.change_name('New Name', mock_branch_uniqueness_service)

        assert branch.name == 'New Name'
        mock_event_bus.add_event.assert_called_once()

    def test_change_name_same_name(self, mock_event_bus: object, mock_branch_uniqueness_service: object) -> None:
        branch = Branch(id='b1', name='Same Name', status=BranchStatus.OPEN.value)

        branch.change_name('Same Name', mock_branch_uniqueness_service)

        assert branch.name == 'Same Name'
        mock_event_bus.add_event.assert_not_called()

    def test_change_name_duplicate(self, mock_event_bus: object, mock_branch_uniqueness_service: object) -> None:
        branch = Branch(id='b1', name='Old Name', status=BranchStatus.OPEN.value)
        mock_branch_uniqueness_service.is_name_unique.return_value = False

        with pytest.raises(BranchNameAlreadyExists):
            branch.change_name('Duplicate', mock_branch_uniqueness_service)

    def test_assign_manager(self, mock_event_bus: object, mock_branch_assignment_service: object) -> None:
        branch = Branch(id='b1', name='Test Branch', status=BranchStatus.OPEN.value)

        branch.assign_manager('manager1', mock_branch_assignment_service)

        assert branch.manager_id == 'manager1'
        assert branch.status == BranchStatus.ACTIVE.value
        mock_event_bus.add_event.assert_called_once()

    def test_assign_manager_not_manager(self, mock_event_bus: object, mock_branch_assignment_service: object) -> None:
        branch = Branch(id='b1', name='Test Branch', status=BranchStatus.OPEN.value)
        mock_branch_assignment_service.can_assign_manager.return_value = False

        with pytest.raises(StaffNotManager):
            branch.assign_manager('librarian1', mock_branch_assignment_service)

    def test_close_branch(self, mock_event_bus: object) -> None:
        branch = Branch(id='b1', name='Test Branch', status=BranchStatus.OPEN.value)

        branch.close()

        assert branch.status == BranchStatus.CLOSED.value
        mock_event_bus.add_event.assert_called_once()

    def test_close_already_closed_branch(self, mock_event_bus: object) -> None:
        branch = Branch(id='b1', name='Test Branch', status=BranchStatus.CLOSED.value)

        with pytest.raises(BranchAlreadyClosed):
            branch.close()


class TestStaff:
    def test_create_staff(self, mock_event_bus: object, mock_staff_uniqueness_service: object) -> None:
        staff = Staff.create(
            name='John Librarian',
            email='john@library.org',
            role=StaffRole.LIBRARIAN.value,
            staff_uniqueness_service=mock_staff_uniqueness_service,
        )

        assert staff.name == 'John Librarian'
        assert staff.email == 'john@library.org'
        assert staff.role == StaffRole.LIBRARIAN.value
        assert staff.status == StaffStatus.ACTIVE.value
        assert staff.hire_date == datetime.date.today()

    def test_create_staff_manager(self, mock_event_bus: object, mock_staff_uniqueness_service: object) -> None:
        staff = Staff.create(
            name='Jane Manager',
            email='jane@library.org',
            role=StaffRole.MANAGER.value,
            staff_uniqueness_service=mock_staff_uniqueness_service,
        )

        assert staff.role == StaffRole.MANAGER.value

    def test_create_staff_duplicate_email(self, mock_event_bus: object, mock_staff_uniqueness_service: object) -> None:
        mock_staff_uniqueness_service.is_email_unique.return_value = False

        with pytest.raises(StaffEmailAlreadyExists):
            Staff.create(
                name='Test Staff',
                email='duplicate@library.org',
                role=StaffRole.LIBRARIAN.value,
                staff_uniqueness_service=mock_staff_uniqueness_service,
            )

    def test_change_email(self, mock_event_bus: object, mock_staff_uniqueness_service: object) -> None:
        staff = Staff(id='s1', name='Test Staff', email='old@library.org', role=StaffRole.LIBRARIAN.value)

        staff.change_email('new@library.org', mock_staff_uniqueness_service)

        assert staff.email == 'new@library.org'
        mock_event_bus.add_event.assert_called_once()

    def test_change_email_same_email(self, mock_event_bus: object, mock_staff_uniqueness_service: object) -> None:
        staff = Staff(id='s1', name='Test Staff', email='same@library.org', role=StaffRole.LIBRARIAN.value)

        staff.change_email('same@library.org', mock_staff_uniqueness_service)

        assert staff.email == 'same@library.org'
        mock_event_bus.add_event.assert_not_called()

    def test_change_email_duplicate(self, mock_event_bus: object, mock_staff_uniqueness_service: object) -> None:
        staff = Staff(id='s1', name='Test Staff', email='old@library.org', role=StaffRole.LIBRARIAN.value)
        mock_staff_uniqueness_service.is_email_unique.return_value = False

        with pytest.raises(StaffEmailAlreadyExists):
            staff.change_email('duplicate@library.org', mock_staff_uniqueness_service)

    def test_change_role(self, mock_event_bus: object) -> None:
        staff = Staff(id='s1', name='Test Staff', email='test@library.org', role=StaffRole.LIBRARIAN.value)

        staff.change_role(StaffRole.MANAGER.value)

        assert staff.role == StaffRole.MANAGER.value

    def test_mark_as_inactive(self, mock_event_bus: object) -> None:
        staff = Staff(
            id='s1',
            name='Test Staff',
            email='test@library.org',
            role=StaffRole.LIBRARIAN.value,
            status=StaffStatus.ACTIVE.value,
        )

        staff.mark_as_inactive()

        assert staff.status == StaffStatus.INACTIVE.value

    def test_mark_as_inactive_not_active(self, mock_event_bus: object) -> None:
        staff = Staff(
            id='s1',
            name='Test Staff',
            email='test@library.org',
            role=StaffRole.LIBRARIAN.value,
            status=StaffStatus.INACTIVE.value,
        )

        with pytest.raises(StaffNotActive):
            staff.mark_as_inactive()
