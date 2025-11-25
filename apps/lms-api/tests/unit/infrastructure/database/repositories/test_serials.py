"""Unit tests for serials repositories - function-based with 100% coverage."""

from unittest.mock import Mock, patch

import pytest
import sqlalchemy.exc as sa_exc

from tests.unit.factories import SerialFactory, SerialIssueFactory
from lms.infrastructure.database import RepositoryError
from lms.infrastructure.database.repositories.serials import SQLAlchemySerialRepository, SQLAlchemySerialIssueRepository


# Fixtures
@pytest.fixture
def mock_session() -> Mock:
    return Mock()


# SQLAlchemySerialRepository Tests
def test_serial_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_serial1 = SerialFactory.build()
    mock_serial2 = SerialFactory.build()
    mock_session.query.return_value.all.return_value = [mock_serial1, mock_serial2]

    with patch('lms.infrastructure.database.repositories.serials.SerialMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        serials = repo.find_all()

        assert len(serials) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_serial_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve serials'):
        repo.find_all()


def test_serial_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_serial = SerialFactory.build()
    mock_session.get.return_value = mock_serial

    with patch('lms.infrastructure.database.repositories.serials.SerialMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_serial
        serial = repo.get_by_id('serial1')

        assert serial == mock_serial
        mock_session.get.assert_called_once()


def test_serial_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_session.get.return_value = None

    serial = repo.get_by_id('nonexistent')

    assert serial is None


def test_serial_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve serial'):
        repo.get_by_id('serial1')


def test_serial_save_new_serial(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_serial = Mock()
    mock_serial.id = None
    mock_model = SerialFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.serials.SerialMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_serial)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert mock_serial.id == str(mock_model.id)


def test_serial_save_new_serial_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_serial = Mock()
    mock_serial.id = None
    mock_model = SerialFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB error')

    with patch('lms.infrastructure.database.repositories.serials.SerialMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save serial'):
            repo.save(mock_serial)

        mock_session.rollback.assert_called_once()


def test_serial_save_existing_serial(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_serial = Mock()
    mock_serial.id = 'serial1'
    mock_serial.title = 'Updated Serial'
    mock_serial.issn = '1234-5678'
    mock_serial.frequency = 'monthly'
    mock_serial.description = 'Updated description'
    mock_serial.status = 'active'

    mock_model = Mock()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_serial)

    assert mock_model.title == 'Updated Serial'
    assert mock_model.issn == '1234-5678'
    mock_session.commit.assert_called_once()
    assert result == mock_serial


def test_serial_save_existing_serial_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_serial = Mock()
    mock_serial.id = 'serial1'
    mock_serial.title = 'Updated'
    mock_serial.issn = '1234-5678'
    mock_serial.frequency = 'monthly'
    mock_serial.description = 'Description'
    mock_serial.status = 'active'

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to save serial'):
        repo.save(mock_serial)

    mock_session.rollback.assert_called_once()


def test_serial_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)

    repo.delete_by_id('serial1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_serial_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete serial'):
        repo.delete_by_id('serial1')

    mock_session.rollback.assert_called_once()


# SQLAlchemySerialIssueRepository Tests
def test_serial_issue_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_issue1 = SerialIssueFactory.build()
    mock_issue2 = SerialIssueFactory.build()
    mock_session.query.return_value.all.return_value = [mock_issue1, mock_issue2]

    with patch('lms.infrastructure.database.repositories.serials.SerialIssueMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        issues = repo.find_all()

        assert len(issues) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_serial_issue_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve serial issues'):
        repo.find_all()


def test_serial_issue_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_issue = SerialIssueFactory.build()
    mock_session.get.return_value = mock_issue

    with patch('lms.infrastructure.database.repositories.serials.SerialIssueMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_issue
        issue = repo.get_by_id('issue1')

        assert issue == mock_issue
        mock_session.get.assert_called_once()


def test_serial_issue_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_session.get.return_value = None

    issue = repo.get_by_id('nonexistent')

    assert issue is None


def test_serial_issue_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve serial issue'):
        repo.get_by_id('issue1')


def test_serial_issue_save_new_issue(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_issue = Mock()
    mock_issue.id = None
    mock_model = SerialIssueFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.serials.SerialIssueMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_issue)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert mock_issue.id == str(mock_model.id)


def test_serial_issue_save_new_issue_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_issue = Mock()
    mock_issue.id = None
    mock_model = SerialIssueFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB error')

    with patch('lms.infrastructure.database.repositories.serials.SerialIssueMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save serial issue'):
            repo.save(mock_issue)

        mock_session.rollback.assert_called_once()


def test_serial_issue_save_existing_issue(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_issue = Mock()
    mock_issue.id = 'issue1'
    mock_issue.issue_number = '42'
    mock_issue.date_received = '2024-01-15'
    mock_issue.status = 'received'

    mock_model = Mock()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_issue)

    assert mock_model.issue_number == '42'
    mock_session.commit.assert_called_once()
    assert result == mock_issue


def test_serial_issue_save_existing_issue_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_issue = Mock()
    mock_issue.id = 'issue1'
    mock_issue.issue_number = '42'
    mock_issue.date_received = '2024-01-15'
    mock_issue.status = 'received'

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to update serial issue'):
        repo.save(mock_issue)

    mock_session.rollback.assert_called_once()


def test_serial_issue_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)

    repo.delete_by_id('issue1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_serial_issue_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemySerialIssueRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete serial issue'):
        repo.delete_by_id('issue1')

    mock_session.rollback.assert_called_once()
