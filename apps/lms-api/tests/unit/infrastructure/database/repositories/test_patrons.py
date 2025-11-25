"""Unit tests for patrons repositories - function-based with 100% coverage."""

from unittest.mock import Mock, patch

import pytest
import sqlalchemy.exc as sa_exc

from tests.unit.factories import FineFactory, PatronFactory
from lms.infrastructure.database import RepositoryError
from lms.infrastructure.database.repositories.patrons import SQLAlchemyFineRepository, SQLAlchemyPatronRepository


# Fixtures
@pytest.fixture
def mock_session() -> Mock:
    return Mock()


# SQLAlchemyPatronRepository Tests
def test_patron_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_patron1 = PatronFactory.build()
    mock_patron2 = PatronFactory.build()
    mock_session.query.return_value.all.return_value = [mock_patron1, mock_patron2]

    with patch('lms.infrastructure.database.repositories.patrons.PatronMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        patrons = repo.find_all()

        assert len(patrons) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_patron_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve patrons'):
        repo.find_all()


def test_patron_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_patron = PatronFactory.build()
    mock_session.get.return_value = mock_patron

    with patch('lms.infrastructure.database.repositories.patrons.PatronMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_patron
        patron = repo.get_by_id('patron1')

        assert patron == mock_patron
        mock_session.get.assert_called_once()


def test_patron_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_session.get.return_value = None

    patron = repo.get_by_id('nonexistent')

    assert patron is None


def test_patron_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve patron'):
        repo.get_by_id('patron1')


def test_patron_exists_by_email_returns_true(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value = Mock()
    mock_session.query.return_value.exists.return_value = Mock()
    mock_session.query.return_value.scalar.return_value = True

    result = repo.exists_by_email('patron@example.com')

    assert result is True


def test_patron_exists_by_email_returns_false(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value = Mock()
    mock_session.query.return_value.exists.return_value = Mock()
    mock_session.query.return_value.scalar.return_value = False

    result = repo.exists_by_email('nonexistent@example.com')

    assert result is False


def test_patron_exists_by_email_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to check patron existence by email'):
        repo.exists_by_email('test@example.com')


def test_patron_save_new_patron(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_patron = Mock()
    mock_patron.id = None
    mock_model = PatronFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.patrons.PatronMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_patron)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert mock_patron.id == str(mock_model.id)


def test_patron_save_new_patron_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_patron = Mock()
    mock_patron.id = None
    mock_model = PatronFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB error')

    with patch('lms.infrastructure.database.repositories.patrons.PatronMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save patron'):
            repo.save(mock_patron)

        mock_session.rollback.assert_called_once()


def test_patron_save_existing_patron(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_patron = Mock()
    mock_patron.id = 'patron1'
    mock_patron.name = 'Updated Patron'
    mock_patron.email = 'updated@example.com'
    mock_patron.phone = '5551234567'
    mock_patron.address = 'New Address'
    mock_patron.status = 'active'

    mock_model = Mock()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_patron)

    assert mock_model.name == 'Updated Patron'
    assert mock_model.email == 'updated@example.com'
    mock_session.commit.assert_called_once()
    assert result == mock_patron


def test_patron_save_existing_patron_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_patron = Mock()
    mock_patron.id = 'patron1'
    mock_patron.name = 'Updated'
    mock_patron.email = 'updated@example.com'
    mock_patron.phone = '555-0123'
    mock_patron.address = 'Address'
    mock_patron.status = 'active'

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to update patron'):
        repo.save(mock_patron)

    mock_session.rollback.assert_called_once()


def test_patron_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)

    repo.delete_by_id('patron1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_patron_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPatronRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete patron'):
        repo.delete_by_id('patron1')

    mock_session.rollback.assert_called_once()


# SQLAlchemyFineRepository Tests
def test_fine_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_fine1 = FineFactory.build()
    mock_fine2 = FineFactory.build()
    mock_session.query.return_value.all.return_value = [mock_fine1, mock_fine2]

    with patch('lms.infrastructure.database.repositories.patrons.FineMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        fines = repo.find_all()

        assert len(fines) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_fine_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve fines'):
        repo.find_all()


def test_fine_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_fine = FineFactory.build()
    mock_session.get.return_value = mock_fine

    with patch('lms.infrastructure.database.repositories.patrons.FineMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_fine
        fine = repo.get_by_id('fine1')

        assert fine == mock_fine
        mock_session.get.assert_called_once()


def test_fine_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_session.get.return_value = None

    fine = repo.get_by_id('nonexistent')

    assert fine is None


def test_fine_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve fine'):
        repo.get_by_id('fine1')


def test_fine_save_new_fine(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_fine = Mock()
    mock_fine.id = None
    mock_model = FineFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.patrons.FineMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_fine)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert mock_fine.id == str(mock_model.id)


def test_fine_save_new_fine_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_fine = Mock()
    mock_fine.id = None
    mock_model = FineFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB error')

    with patch('lms.infrastructure.database.repositories.patrons.FineMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save fine'):
            repo.save(mock_fine)

        mock_session.rollback.assert_called_once()


def test_fine_save_existing_fine(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_fine = Mock()
    mock_fine.id = 'fine1'
    mock_fine.paid_date = None
    mock_fine.status = 'unpaid'

    mock_model = Mock()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_fine)

    assert mock_model.paid_date is None
    mock_session.commit.assert_called_once()
    assert result == mock_fine


def test_fine_save_existing_fine_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_fine = Mock()
    mock_fine.id = 'fine1'
    mock_fine.paid_date = None
    mock_fine.status = 'unpaid'

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to update fine'):
        repo.save(mock_fine)

    mock_session.rollback.assert_called_once()


def test_fine_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)

    repo.delete_by_id('fine1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_fine_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyFineRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete fine'):
        repo.delete_by_id('fine1')

    mock_session.rollback.assert_called_once()
