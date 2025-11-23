from __future__ import annotations

from unittest.mock import ANY, Mock, MagicMock, patch

import pytest

from lms.app.services.patrons import FineService, PatronService
from lms.domain.patrons.entities import Fine, Patron
from lms.domain.patrons.exceptions import PatronDoesNotExistError


@pytest.fixture
def mock_patron_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_fine_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_patron_uniqueness_service() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_patron_reinstatement_service() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_fine_policy_service() -> Mock:
    return MagicMock()


@pytest.fixture
def patron_service(
    mock_patron_repository: Mock, mock_patron_uniqueness_service: Mock, mock_patron_reinstatement_service: Mock
) -> PatronService:
    return PatronService(
        patron_repository=mock_patron_repository,
        patron_uniqueness_service=mock_patron_uniqueness_service,
        patron_reinstatement_service=mock_patron_reinstatement_service,
    )


@pytest.fixture
def fine_service(mock_fine_repository: Mock, mock_fine_policy_service: Mock) -> FineService:
    return FineService(fine_repository=mock_fine_repository, fine_policy_service=mock_fine_policy_service)


def test_patron_service_find_all_patrons(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    mock_patrons = [Mock(spec=Patron), Mock(spec=Patron)]
    mock_patron_repository.find_all.return_value = mock_patrons

    result = patron_service.find_all_patrons()

    assert result == mock_patrons
    mock_patron_repository.find_all.assert_called_once()


def test_patron_service_get_patron_success(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    patron = Mock(spec=Patron, id='patron-123')
    mock_patron_repository.get_by_id.return_value = patron

    result = patron_service.get_patron('patron-123')

    assert result == patron
    mock_patron_repository.get_by_id.assert_called_once_with('patron-123')


def test_patron_service_get_patron_not_found(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    mock_patron_repository.get_by_id.return_value = None

    with pytest.raises(PatronDoesNotExistError):
        patron_service.get_patron('patron-999')


@patch('lms.app.services.patrons.Patron')
def test_patron_service_create_patron(
    mock_patron_class: Mock, patron_service: PatronService, mock_patron_repository: Mock
) -> None:
    patron = MagicMock()
    mock_patron_class.create.return_value = patron
    mock_patron_repository.save.return_value = patron

    result = patron_service.create_patron(branch_id='branch-123', name='Jane Doe', email='jane@example.com')

    assert result == patron
    mock_patron_class.create.assert_called_once_with(
        branch_id='branch-123', name='Jane Doe', email='jane@example.com', patron_uniqueness_service=ANY
    )
    patron.activate.assert_called_once()
    mock_patron_repository.save.assert_called_once_with(patron)


def test_patron_service_update_patron(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    patron = Mock(spec=Patron, id='patron-123', name='Old Name')
    mock_patron_repository.get_by_id.return_value = patron
    mock_patron_repository.save.return_value = patron

    result = patron_service.update_patron('patron-123', 'New Name')

    assert result == patron
    assert patron.name == 'New Name'


def test_patron_service_update_patron_email(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    patron = Mock(spec=Patron, id='patron-123')
    mock_patron_repository.get_by_id.return_value = patron
    mock_patron_repository.save.return_value = patron

    result = patron_service.update_patron_email('patron-123', 'newemail@example.com')

    assert result == patron
    patron.change_email.assert_called_once()


def test_patron_service_activate_patron(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    patron = Mock(spec=Patron, id='patron-123')
    mock_patron_repository.get_by_id.return_value = patron
    mock_patron_repository.save.return_value = patron

    result = patron_service.activate_patron('patron-123')

    assert result == patron
    patron.activate.assert_called_once()


def test_patron_service_reinstate_patron(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    patron = Mock(spec=Patron, id='patron-123')
    mock_patron_repository.get_by_id.return_value = patron
    mock_patron_repository.save.return_value = patron

    result = patron_service.reinstate_patron('patron-123')

    assert result == patron
    patron.reinstate.assert_called_once()


def test_patron_service_archive_patron(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    patron = Mock(spec=Patron, id='patron-123')
    mock_patron_repository.get_by_id.return_value = patron
    mock_patron_repository.save.return_value = patron

    result = patron_service.archive_patron('patron-123')

    assert result == patron
    patron.archive.assert_called_once()


def test_patron_service_unarchive_patron(patron_service: PatronService, mock_patron_repository: Mock) -> None:
    patron = Mock(spec=Patron, id='patron-123')
    mock_patron_repository.get_by_id.return_value = patron
    mock_patron_repository.save.return_value = patron

    result = patron_service.unarchive_patron('patron-123')

    assert result == patron
    patron.unarchive.assert_called_once()


def test_fine_service_find_all_fines(fine_service: FineService, mock_fine_repository: Mock) -> None:
    mock_fines = [Mock(spec=Fine), Mock(spec=Fine)]
    mock_fine_repository.find_all.return_value = mock_fines

    result = fine_service.find_all_fines()

    assert result == mock_fines
    mock_fine_repository.find_all.assert_called_once()


def test_fine_service_get_fine_success(fine_service: FineService, mock_fine_repository: Mock) -> None:
    fine = Mock(spec=Fine, id='fine-123')
    mock_fine_repository.get_by_id.return_value = fine

    result = fine_service.get_fine('fine-123')

    assert result == fine
    mock_fine_repository.get_by_id.assert_called_once_with('fine-123')


def test_fine_service_get_fine_not_found(fine_service: FineService, mock_fine_repository: Mock) -> None:
    mock_fine_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Fine with id fine-999 not found'):
        fine_service.get_fine('fine-999')


def test_fine_service_pay_fine(fine_service: FineService, mock_fine_repository: Mock) -> None:
    fine = Mock(spec=Fine, id='fine-123')
    mock_fine_repository.get_by_id.return_value = fine
    mock_fine_repository.save.return_value = fine

    result = fine_service.pay_fine('fine-123')

    assert result == fine
    fine.pay.assert_called_once()


def test_fine_service_waive_fine(fine_service: FineService, mock_fine_repository: Mock) -> None:
    fine = Mock(spec=Fine, id='fine-123')
    mock_fine_repository.get_by_id.return_value = fine
    mock_fine_repository.save.return_value = fine

    result = fine_service.waive_fine('fine-123')

    assert result == fine
    fine.waive.assert_called_once()


def test_fine_service_process_overdue_loan(fine_service: FineService, mock_fine_repository: Mock) -> None:
    fine = Mock(spec=Fine)
    mock_fine_repository.save.return_value = fine

    result = fine_service.process_overdue_loan(loan_id='loan-123', patron_id='patron-456', days_late=5)

    assert result == fine
    mock_fine_repository.save.assert_called_once()
