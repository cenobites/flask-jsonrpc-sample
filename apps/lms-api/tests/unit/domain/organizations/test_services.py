from unittest.mock import Mock
from collections.abc import Iterator

import pytest

from lms.domain.organizations.entities import Staff, Branch
from lms.domain.organizations.services import StaffUniquenessService, BranchAssignmentService, BranchUniquenessService
from lms.infrastructure.database.models.organizations import StaffRole


class TestBranchUniquenessService:
    @pytest.fixture
    def mock_branch_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_branch_repository: Iterator) -> Iterator:
        return BranchUniquenessService(branch_repository=mock_branch_repository)

    def test_is_name_unique_when_name_does_not_exist(self, service: object, mock_branch_repository: object) -> None:
        mock_branch_repository.exists_by_name.return_value = False

        result = service.is_name_unique('Downtown Branch')

        assert result is True
        mock_branch_repository.exists_by_name.assert_called_once_with('Downtown Branch')

    def test_is_name_unique_when_name_exists(self, service: object, mock_branch_repository: object) -> None:
        mock_branch_repository.exists_by_name.return_value = True

        result = service.is_name_unique('Main Branch')

        assert result is False
        mock_branch_repository.exists_by_name.assert_called_once_with('Main Branch')


class TestBranchAssignmentService:
    @pytest.fixture
    def mock_branch_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def mock_staff_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_branch_repository: Iterator, mock_staff_repository: Iterator) -> Iterator:
        return BranchAssignmentService(branch_repository=mock_branch_repository, staff_repository=mock_staff_repository)

    def test_can_assign_manager_when_valid(
        self, service: object, mock_branch_repository: object, mock_staff_repository: object
    ) -> None:
        mock_branch = Mock(spec=Branch)
        mock_branch_repository.get_by_id.return_value = mock_branch

        mock_manager = Mock(spec=Staff)
        mock_manager.role = StaffRole.MANAGER.value
        mock_staff_repository.get_by_id.return_value = mock_manager

        result = service.can_assign_manager(branch_id='b1', manager_id='s1')

        assert result is True
        mock_branch_repository.get_by_id.assert_called_once_with('b1')
        mock_staff_repository.get_by_id.assert_called_once_with('s1')

    def test_can_assign_manager_when_branch_not_found(
        self, service: object, mock_branch_repository: object, mock_staff_repository: object
    ) -> None:
        mock_branch_repository.get_by_id.return_value = None

        result = service.can_assign_manager(branch_id='b1', manager_id='s1')

        assert result is False
        mock_branch_repository.get_by_id.assert_called_once_with('b1')
        mock_staff_repository.get_by_id.assert_not_called()

    def test_can_assign_manager_when_staff_not_found(
        self, service: object, mock_branch_repository: object, mock_staff_repository: object
    ) -> None:
        mock_branch = Mock(spec=Branch)
        mock_branch_repository.get_by_id.return_value = mock_branch
        mock_staff_repository.get_by_id.return_value = None

        result = service.can_assign_manager(branch_id='b1', manager_id='s1')

        assert result is False

    def test_can_assign_manager_when_staff_not_manager(
        self, service: object, mock_branch_repository: object, mock_staff_repository: object
    ) -> None:
        mock_branch = Mock(spec=Branch)
        mock_branch_repository.get_by_id.return_value = mock_branch

        mock_staff = Mock(spec=Staff)
        mock_staff.role = StaffRole.LIBRARIAN.value
        mock_staff_repository.get_by_id.return_value = mock_staff

        result = service.can_assign_manager(branch_id='b1', manager_id='s1')

        assert result is False


class TestStaffUniquenessService:
    @pytest.fixture
    def mock_staff_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_staff_repository: Iterator) -> Iterator:
        return StaffUniquenessService(staff_repository=mock_staff_repository)

    def test_is_email_unique_when_email_does_not_exist(self, service: object, mock_staff_repository: object) -> None:
        mock_staff_repository.exists_by_email.return_value = False

        result = service.is_email_unique('new@example.com')

        assert result is True
        mock_staff_repository.exists_by_email.assert_called_once_with('new@example.com')

    def test_is_email_unique_when_email_exists(self, service: object, mock_staff_repository: object) -> None:
        mock_staff_repository.exists_by_email.return_value = True

        result = service.is_email_unique('existing@example.com')

        assert result is False
        mock_staff_repository.exists_by_email.assert_called_once_with('existing@example.com')
