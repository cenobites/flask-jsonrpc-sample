from __future__ import annotations

from unittest.mock import ANY, Mock, MagicMock, patch

import pytest

from lms.app.services.organizations import StaffService, BranchService
from lms.app.exceptions.organizations import StaffNotFoundError, BranchNotFoundError
from lms.domain.organizations.entities import Staff, Branch


@pytest.fixture
def mock_branch_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_staff_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_branch_uniqueness_service() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_branch_assignment_service() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_staff_uniqueness_service() -> Mock:
    return MagicMock()


@pytest.fixture
def branch_service(
    mock_branch_repository: Mock, mock_branch_uniqueness_service: Mock, mock_branch_assignment_service: Mock
) -> BranchService:
    return BranchService(
        branch_repository=mock_branch_repository,
        branch_uniqueness_service=mock_branch_uniqueness_service,
        branch_assignment_service=mock_branch_assignment_service,
    )


@pytest.fixture
def staff_service(mock_staff_repository: Mock, mock_staff_uniqueness_service: Mock) -> StaffService:
    return StaffService(staff_repository=mock_staff_repository, staff_uniqueness_service=mock_staff_uniqueness_service)


def test_branch_service_find_all_branches(branch_service: BranchService, mock_branch_repository: Mock) -> None:
    mock_branches = [Mock(spec=Branch), Mock(spec=Branch)]
    mock_branch_repository.find_all.return_value = mock_branches

    result = branch_service.find_all_branches()

    assert result == mock_branches
    mock_branch_repository.find_all.assert_called_once()


def test_branch_service_get_branch_success(branch_service: BranchService, mock_branch_repository: Mock) -> None:
    branch = Mock(spec=Branch, id='branch-123')
    mock_branch_repository.get_by_id.return_value = branch

    result = branch_service.get_branch('branch-123')

    assert result == branch
    mock_branch_repository.get_by_id.assert_called_once_with('branch-123')


def test_branch_service_get_branch_not_found(branch_service: BranchService, mock_branch_repository: Mock) -> None:
    mock_branch_repository.get_by_id.return_value = None

    with pytest.raises(BranchNotFoundError):
        branch_service.get_branch('branch-999')


def test_branch_service_create_branch_without_manager(
    branch_service: BranchService, mock_branch_repository: Mock
) -> None:
    branch = Mock(spec=Branch)
    mock_branch_repository.save.return_value = branch

    result = branch_service.create_branch(name='Downtown Library', address='123 Main St')

    assert result == branch
    mock_branch_repository.save.assert_called_once()


@patch('lms.app.services.organizations.Branch')
def test_branch_service_create_branch_with_manager(
    mock_branch_class: Mock,
    branch_service: BranchService,
    mock_branch_repository: Mock,
    mock_branch_assignment_service: Mock,
) -> None:
    branch = MagicMock()
    mock_branch_class.create.return_value = branch
    mock_branch_repository.save.return_value = branch

    result = branch_service.create_branch(name='Central Library', manager_id='mgr-123')

    assert result == branch
    mock_branch_class.create.assert_called_once_with(
        name='Central Library', email=None, address=None, phone=None, branch_uniqueness_service=ANY
    )
    branch.assign_manager.assert_called_once_with('mgr-123', mock_branch_assignment_service)
    mock_branch_repository.save.assert_called_once_with(branch)


def test_branch_service_update_branch(branch_service: BranchService, mock_branch_repository: Mock) -> None:
    branch = Mock(spec=Branch, id='branch-123', name='Old Name', address='Old Address')
    mock_branch_repository.get_by_id.return_value = branch
    mock_branch_repository.save.return_value = branch

    result = branch_service.update_branch('branch-123', name='New Name', address='New Address')

    assert result == branch
    branch.change_name.assert_called_once()
    assert branch.address == 'New Address'
    mock_branch_repository.save.assert_called_once()


def test_branch_service_update_branch_partial(branch_service: BranchService, mock_branch_repository: Mock) -> None:
    branch = Mock(spec=Branch)
    branch.id = 'branch-123'
    branch.name = 'Old Name'
    branch.phone = '555-1234'
    branch.address = None
    branch.email = None
    mock_branch_repository.get_by_id.return_value = branch
    mock_branch_repository.save.return_value = branch

    result = branch_service.update_branch('branch-123', phone='555-9999')

    assert result == branch
    assert branch.phone == '555-9999'


def test_branch_service_assign_manager(branch_service: BranchService, mock_branch_repository: Mock) -> None:
    branch = Mock(spec=Branch, id='branch-123')
    mock_branch_repository.get_by_id.return_value = branch
    mock_branch_repository.save.return_value = branch

    result = branch_service.assign_branch_manager('branch-123', 'mgr-456')

    assert result == branch
    branch.assign_manager.assert_called_once()


def test_branch_service_close_branch(branch_service: BranchService, mock_branch_repository: Mock) -> None:
    branch = Mock(spec=Branch, id='branch-123')
    mock_branch_repository.get_by_id.return_value = branch
    mock_branch_repository.save.return_value = branch

    result = branch_service.close_branch('branch-123')

    assert result == branch
    branch.close.assert_called_once()


def test_staff_service_find_all_staff(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    mock_staff = [Mock(spec=Staff), Mock(spec=Staff)]
    mock_staff_repository.find_all.return_value = mock_staff

    result = staff_service.find_all_staff()

    assert result == mock_staff
    mock_staff_repository.find_all.assert_called_once()


def test_staff_service_get_staff_success(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    staff = Mock(spec=Staff, id='staff-123')
    mock_staff_repository.get_by_id.return_value = staff

    result = staff_service.get_staff('staff-123')

    assert result == staff
    mock_staff_repository.get_by_id.assert_called_once_with('staff-123')


def test_staff_service_get_staff_not_found(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    mock_staff_repository.get_by_id.return_value = None

    with pytest.raises(StaffNotFoundError):
        staff_service.get_staff('staff-999')


def test_staff_service_create_staff(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    staff = Mock(spec=Staff)
    mock_staff_repository.save.return_value = staff

    result = staff_service.create_staff(name='John Doe', email='john@library.com', role='librarian')

    assert result == staff
    mock_staff_repository.save.assert_called_once()


def test_staff_service_update_staff_name(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    staff = Mock(spec=Staff, id='staff-123', name='Old Name')
    mock_staff_repository.get_by_id.return_value = staff
    mock_staff_repository.save.return_value = staff

    result = staff_service.update_staff('staff-123', name='New Name')

    assert result == staff
    assert staff.name == 'New Name'


def test_staff_service_update_staff_email(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    staff = Mock(spec=Staff, id='staff-123')
    mock_staff_repository.get_by_id.return_value = staff
    mock_staff_repository.save.return_value = staff

    result = staff_service.update_staff_email('staff-123', 'new@library.com')

    assert result == staff
    staff.change_email.assert_called_once()


def test_staff_service_assign_to_branch(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    staff = Mock(spec=Staff, id='staff-123')
    mock_staff_repository.get_by_id.return_value = staff
    mock_staff_repository.save.return_value = staff

    result = staff_service.assign_staff_to_branch('staff-123', 'branch-456')

    assert result == staff
    assert staff.branch_id == 'branch-456'


def test_staff_service_assign_role(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    staff = Mock(spec=Staff, id='staff-123')
    mock_staff_repository.get_by_id.return_value = staff
    mock_staff_repository.save.return_value = staff

    result = staff_service.assign_staff_role('staff-123', 'manager')

    assert result == staff
    staff.change_role.assert_called_once_with('manager')


def test_staff_service_inactivate_staff(staff_service: StaffService, mock_staff_repository: Mock) -> None:
    staff = Mock(spec=Staff, id='staff-123')
    mock_staff_repository.get_by_id.return_value = staff
    mock_staff_repository.save.return_value = staff

    result = staff_service.inactivate_staff('staff-123')

    assert result == staff
    staff.mark_as_inactive.assert_called_once()
