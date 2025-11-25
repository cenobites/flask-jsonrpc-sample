"""Unit tests for circulations repositories - function-based with 100% coverage."""

from unittest.mock import Mock, patch

import pytest
import sqlalchemy.exc as sa_exc

from tests.unit.factories import HoldFactory, LoanFactory
from lms.infrastructure.database import RepositoryError
from lms.infrastructure.database.repositories.circulations import SQLAlchemyHoldRepository, SQLAlchemyLoanRepository


# Fixtures
@pytest.fixture
def mock_session() -> Mock:
    return Mock()


# SQLAlchemyLoanRepository Tests
def test_loan_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_loan1 = LoanFactory.build()
    mock_loan2 = LoanFactory.build()
    mock_session.query.return_value.all.return_value = [mock_loan1, mock_loan2]

    with patch('lms.infrastructure.database.repositories.circulations.LoanMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        loans = repo.find_all()

        assert len(loans) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_loan_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve loans'):
        repo.find_all()


def test_loan_find_by_patron_id(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_loan1 = LoanFactory.build()
    mock_loan2 = LoanFactory.build()
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value.all.return_value = [mock_loan1, mock_loan2]

    with patch('lms.infrastructure.database.repositories.circulations.LoanMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        loans = repo.find_by_patron_id('patron1')

        assert len(loans) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_loan_find_by_patron_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_session.query.return_value.filter.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve loans for patron'):
        repo.find_by_patron_id('patron1')


def test_loan_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_loan = LoanFactory.build()
    mock_session.get.return_value = mock_loan

    with patch('lms.infrastructure.database.repositories.circulations.LoanMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_loan
        loan = repo.get_by_id('loan1')

        assert loan == mock_loan
        mock_session.get.assert_called_once()


def test_loan_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_session.get.return_value = None

    loan = repo.get_by_id('nonexistent')

    assert loan is None


def test_loan_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve loan'):
        repo.get_by_id('loan1')


def test_loan_save_new_loan(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_loan = Mock()
    mock_loan.id = None
    mock_loan.staff_out_id = 'staff1'
    mock_loan.staff_in_id = None
    mock_loan.return_date = None

    mock_copy = Mock()
    mock_copy.id = 'copy1'
    mock_copy.status = 'checked_out'

    mock_loan_model = LoanFactory.build()
    mock_copy_model = Mock()

    with patch('lms.infrastructure.database.repositories.circulations.CopyModel'):

        def get_side_effect(model_class: Mock, id_val: str) -> Mock | None:
            if id_val == 'copy1':
                return mock_copy_model
            return None

        mock_session.get.side_effect = get_side_effect

        with patch('lms.infrastructure.database.repositories.circulations.LoanMapper') as mock_mapper:
            mock_mapper.from_entity.return_value = mock_loan_model
            repo.save(mock_loan, mock_copy)

            mock_session.add.assert_called_once_with(mock_loan_model)
            assert mock_session.commit.call_count >= 1
            assert mock_loan.id == str(mock_loan_model.id)


def test_loan_save_new_loan_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_loan = Mock()
    mock_loan.id = None

    mock_copy = Mock()
    mock_copy.id = 'copy1'
    mock_copy.status = 'checked_out'

    mock_copy_model = Mock()

    with patch('lms.infrastructure.database.repositories.circulations.CopyModel'):

        def get_side_effect(model_class: Mock, id_val: str) -> Mock | None:
            if id_val == 'copy1':
                return mock_copy_model
            return None

        mock_session.get.side_effect = get_side_effect
        mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

        with patch('lms.infrastructure.database.repositories.circulations.LoanMapper') as mock_mapper:
            mock_mapper.from_entity.return_value = Mock()

            with pytest.raises(RepositoryError, match='Failed to save loan'):
                repo.save(mock_loan, mock_copy)

            mock_session.rollback.assert_called_once()


def test_loan_save_copy_status_update_error(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_loan = Mock()
    mock_loan.id = None

    mock_copy = Mock()
    mock_copy.id = 'copy1'
    mock_copy.status = 'checked_out'

    with patch('lms.infrastructure.database.repositories.circulations.CopyModel'):
        mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

        with pytest.raises(RepositoryError, match='Failed to update copy status during loan save'):
            repo.save(mock_loan, mock_copy)


def test_loan_save_existing_loan(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_loan = Mock()
    mock_loan.id = 'loan1'
    mock_loan.staff_out_id = '12345678-1234-5678-1234-567812345678'
    mock_loan.staff_in_id = '87654321-4321-8765-4321-876543218765'
    mock_loan.return_date = '2024-01-15'

    mock_copy = Mock()
    mock_copy.id = 'copy1'
    mock_copy.status = 'available'

    mock_loan_model = LoanFactory.build()
    mock_copy_model = Mock()

    with patch('lms.infrastructure.database.repositories.circulations.CopyModel'):

        def get_side_effect(model_class: Mock, id_val: str) -> Mock | None:
            if id_val == 'copy1':
                return mock_copy_model
            elif id_val == 'loan1':
                return mock_loan_model
            return None

        mock_session.get.side_effect = get_side_effect
        result = repo.save(mock_loan, mock_copy)

        assert mock_session.commit.call_count >= 1
        assert result == mock_loan


def test_loan_save_existing_loan_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_loan = Mock()
    mock_loan.id = 'loan1'
    mock_loan.staff_out_id = '12345678-1234-5678-1234-567812345678'
    mock_loan.staff_in_id = None
    mock_loan.return_date = None

    mock_copy = Mock()
    mock_copy.id = 'copy1'
    mock_copy.status = 'available'

    mock_loan_model = Mock()
    mock_copy_model = Mock()

    with patch('lms.infrastructure.database.repositories.circulations.CopyModel'):
        call_count = [0]

        def get_side_effect(model_class: Mock, id_val: str) -> Mock | None:
            call_count[0] += 1
            if call_count[0] == 1:  # First call for copy
                return mock_copy_model
            elif call_count[0] == 2:  # Second call for loan
                return mock_loan_model
            return None

        mock_session.get.side_effect = get_side_effect
        mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

        with pytest.raises(RepositoryError, match='Failed to update loan'):
            repo.save(mock_loan, mock_copy)

        mock_session.rollback.assert_called_once()


def test_loan_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)

    repo.delete_by_id('loan1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_loan_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyLoanRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete loan'):
        repo.delete_by_id('loan1')

    mock_session.rollback.assert_called_once()


# SQLAlchemyHoldRepository Tests
def test_hold_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_hold1 = HoldFactory.build()
    mock_hold2 = HoldFactory.build()
    mock_session.query.return_value.all.return_value = [mock_hold1, mock_hold2]

    with patch('lms.infrastructure.database.repositories.circulations.HoldMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        holds = repo.find_all()

        assert len(holds) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_hold_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve holds'):
        repo.find_all()


def test_hold_find_active_holds_by_patron(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_hold1 = HoldFactory.build()
    mock_hold2 = HoldFactory.build()
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value.all.return_value = [mock_hold1, mock_hold2]

    with patch('lms.infrastructure.database.repositories.circulations.HoldMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        holds = repo.find_active_holds_by_patron('patron1')

        assert len(holds) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_hold_find_active_holds_by_patron_raises_repository_error(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_session.query.return_value.filter.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve active holds for patron'):
        repo.find_active_holds_by_patron('patron1')


def test_hold_find_active_holds_by_item(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_hold1 = HoldFactory.build()
    mock_hold2 = HoldFactory.build()
    mock_query = Mock()
    mock_session.query.return_value = mock_query
    mock_query.join.return_value.filter.return_value.all.return_value = [mock_hold1, mock_hold2]

    with patch('lms.infrastructure.database.repositories.circulations.HoldMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        holds = repo.find_active_holds_by_item('item1')

        assert len(holds) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_hold_find_active_holds_by_item_raises_repository_error(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_session.query.return_value.join.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve active holds for item'):
        repo.find_active_holds_by_item('item1')


def test_hold_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_hold = HoldFactory.build()
    mock_session.get.return_value = mock_hold

    with patch('lms.infrastructure.database.repositories.circulations.HoldMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_hold
        hold = repo.get_by_id('hold1')

        assert hold == mock_hold
        mock_session.get.assert_called_once()


def test_hold_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_session.get.return_value = None

    hold = repo.get_by_id('nonexistent')

    assert hold is None


def test_hold_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve hold'):
        repo.get_by_id('hold1')


def test_hold_save_new_hold(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_hold = Mock()
    mock_hold.id = None
    mock_model = HoldFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.circulations.HoldMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_hold)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert mock_hold.id == str(mock_model.id)


def test_hold_save_new_hold_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_hold = Mock()
    mock_hold.id = None
    mock_model = HoldFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.circulations.HoldMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save hold'):
            repo.save(mock_hold)

        mock_session.rollback.assert_called_once()


def test_hold_save_existing_hold(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_hold = Mock()
    mock_hold.id = 'hold1'
    mock_hold.status = 'fulfilled'
    mock_hold.expiry_date = '2024-01-20'

    mock_model = HoldFactory.build()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_hold)

    mock_session.commit.assert_called_once()
    assert result == mock_hold


def test_hold_save_existing_hold_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_hold = Mock()
    mock_hold.id = 'hold1'
    mock_hold.status = 'fulfilled'
    mock_hold.expiry_date = '2024-01-20'

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to update hold'):
        repo.save(mock_hold)

    mock_session.rollback.assert_called_once()


def test_hold_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)

    repo.delete_by_id('hold1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_hold_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyHoldRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete hold'):
        repo.delete_by_id('hold1')

    mock_session.rollback.assert_called_once()
