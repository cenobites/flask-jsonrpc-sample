"""Unit tests for organizations repositories - function-based with 100% coverage."""

from unittest.mock import Mock, patch

import pytest
import sqlalchemy.exc as sa_exc

from tests.unit.factories import StaffFactory, BranchFactory
from lms.infrastructure.database import RepositoryError
from lms.infrastructure.database.models.organizations import StaffRole
from lms.infrastructure.database.repositories.organizations import SQLAlchemyStaffRepository, SQLAlchemyBranchRepository


# Fixtures
@pytest.fixture
def mock_session() -> Mock:
    return Mock()


# SQLAlchemyBranchRepository Tests
def test_branch_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_branch1 = BranchFactory.build()
    mock_branch2 = BranchFactory.build()
    mock_session.query.return_value.all.return_value = [mock_branch1, mock_branch2]

    with patch('lms.infrastructure.database.repositories.organizations.BranchMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        branches = repo.find_all()

        assert len(branches) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_branch_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve branches'):
        repo.find_all()


def test_branch_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_branch = BranchFactory.build()
    mock_session.get.return_value = mock_branch

    with patch('lms.infrastructure.database.repositories.organizations.BranchMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_branch
        branch = repo.get_by_id('branch1')

        assert branch == mock_branch
        mock_session.get.assert_called_once()


def test_branch_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_session.get.return_value = None

    branch = repo.get_by_id('nonexistent')

    assert branch is None


def test_branch_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve branch'):
        repo.get_by_id('branch1')


def test_branch_exists_by_name_returns_true(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value = Mock()
    mock_session.query.return_value.exists.return_value = Mock()
    mock_session.query.return_value.scalar.return_value = True

    result = repo.exists_by_name('Main Branch')

    assert result is True


def test_branch_exists_by_name_returns_false(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value = Mock()
    mock_session.query.return_value.exists.return_value = Mock()
    mock_session.query.return_value.scalar.return_value = False

    result = repo.exists_by_name('Nonexistent Branch')

    assert result is False


def test_branch_exists_by_name_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to check branch existence by name'):
        repo.exists_by_name('Branch')


def test_branch_save_new_branch(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_branch = Mock()
    mock_branch.id = None
    mock_model = BranchFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.organizations.BranchMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_branch)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert mock_branch.id == str(mock_model.id)


def test_branch_save_new_branch_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_branch = Mock()
    mock_branch.id = None
    mock_model = BranchFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB error')

    with patch('lms.infrastructure.database.repositories.organizations.BranchMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save branch'):
            repo.save(mock_branch)

        mock_session.rollback.assert_called_once()


def test_branch_save_existing_branch(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_branch = Mock()
    mock_branch.id = 'branch1'
    mock_branch.name = 'Updated Branch'
    mock_branch.address = 'New Address'
    mock_branch.phone = '555-0123'
    mock_branch.email = 'branch@example.com'
    mock_branch.manager_id = '12345678-1234-5678-1234-567812345678'
    mock_branch.status = 'active'

    mock_model = Mock()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_branch)

    assert mock_model.name == 'Updated Branch'
    mock_session.commit.assert_called_once()
    assert result == mock_branch


def test_branch_save_existing_branch_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_branch = Mock()
    mock_branch.id = 'branch1'
    mock_branch.name = 'Updated'
    mock_branch.address = 'Address'
    mock_branch.phone = '555-0123'
    mock_branch.email = 'email@example.com'
    mock_branch.manager_id = None
    mock_branch.status = 'active'

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to update branch'):
        repo.save(mock_branch)

    mock_session.rollback.assert_called_once()


def test_branch_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)

    repo.delete_by_id('branch1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_branch_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyBranchRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete branch'):
        repo.delete_by_id('branch1')

    mock_session.rollback.assert_called_once()


# SQLAlchemyStaffRepository Tests
def test_staff_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_staff1 = StaffFactory.build()
    mock_staff2 = StaffFactory.build()
    mock_session.query.return_value.all.return_value = [mock_staff1, mock_staff2]

    with patch('lms.infrastructure.database.repositories.organizations.StaffMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        staff_list = repo.find_all()

        assert len(staff_list) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_staff_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve staff'):
        repo.find_all()


def test_staff_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_staff = StaffFactory.build()
    mock_session.get.return_value = mock_staff

    with patch('lms.infrastructure.database.repositories.organizations.StaffMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_staff
        staff = repo.get_by_id('staff1')

        assert staff == mock_staff
        mock_session.get.assert_called_once()


def test_staff_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_session.get.return_value = None

    staff = repo.get_by_id('nonexistent')

    assert staff is None


def test_staff_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve staff member'):
        repo.get_by_id('staff1')


def test_staff_exists_by_email_returns_true(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value = Mock()
    mock_session.query.return_value.exists.return_value = Mock()
    mock_session.query.return_value.scalar.return_value = True

    result = repo.exists_by_email('test@example.com')

    assert result is True


def test_staff_exists_by_email_returns_false(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value = Mock()
    mock_session.query.return_value.exists.return_value = Mock()
    mock_session.query.return_value.scalar.return_value = False

    result = repo.exists_by_email('nonexistent@example.com')

    assert result is False


def test_staff_exists_by_email_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to check staff existence by email'):
        repo.exists_by_email('test@example.com')


def test_staff_save_new_staff(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_staff = Mock()
    mock_staff.id = None
    mock_model = StaffFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.organizations.StaffMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_staff)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert mock_staff.id == str(mock_model.id)


def test_staff_save_new_staff_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_staff = Mock()
    mock_staff.id = None
    mock_model = StaffFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.organizations.StaffMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save staff member'):
            repo.save(mock_staff)

        mock_session.rollback.assert_called_once()


def test_staff_save_existing_staff(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_staff = Mock()
    mock_staff.id = 'staff1'
    mock_staff.name = 'Updated Name'
    mock_staff.email = 'updated@example.com'
    mock_staff.role = StaffRole.MANAGER.value
    mock_staff.branch_id = '12345678-1234-5678-1234-567812345678'

    mock_model = Mock()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_staff)

    assert mock_model.name == 'Updated Name'
    assert mock_model.email == 'updated@example.com'
    mock_session.commit.assert_called_once()
    assert result == mock_staff


def test_staff_save_existing_staff_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_staff = Mock()
    mock_staff.id = 'staff1'
    mock_staff.name = 'Updated'
    mock_staff.email = 'updated@example.com'
    mock_staff.role = 'manager'
    mock_staff.branch_id = None

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to update staff member'):
        repo.save(mock_staff)

    mock_session.rollback.assert_called_once()


def test_staff_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)

    repo.delete_by_id('staff1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_staff_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyStaffRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete staff member'):
        repo.delete_by_id('staff1')

    mock_session.rollback.assert_called_once()
