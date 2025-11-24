from __future__ import annotations

from unittest.mock import Mock, MagicMock

import pytest

from lms.app.exceptions.patrons import PatronNotFoundError
from lms.domain.patrons.entities import Patron
from lms.domain.catalogs.entities import Copy
from lms.app.services.circulations import HoldService, LoanService
from lms.domain.circulations.entities import Hold, Loan
from lms.domain.organizations.entities import Staff, Branch


@pytest.fixture
def mock_loan_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_hold_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_patron_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_copy_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_item_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_staff_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_branch_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_loan_policy_service() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_hold_policy_service() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_patron_barring_service() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_patron_holding_service() -> Mock:
    return MagicMock()


@pytest.fixture
def loan_service(
    mock_loan_repository: Mock,
    mock_patron_repository: Mock,
    mock_branch_repository: Mock,
    mock_staff_repository: Mock,
    mock_copy_repository: Mock,
    mock_loan_policy_service: Mock,
    mock_patron_barring_service: Mock,
) -> LoanService:
    return LoanService(
        loan_repository=mock_loan_repository,
        patron_repository=mock_patron_repository,
        branch_repository=mock_branch_repository,
        staff_repository=mock_staff_repository,
        copy_repository=mock_copy_repository,
        loan_policy_service=mock_loan_policy_service,
        patron_barring_service=mock_patron_barring_service,
    )


@pytest.fixture
def hold_service(
    mock_hold_repository: Mock,
    mock_patron_repository: Mock,
    mock_item_repository: Mock,
    mock_copy_repository: Mock,
    mock_loan_repository: Mock,
    mock_staff_repository: Mock,
    mock_branch_repository: Mock,
    mock_patron_holding_service: Mock,
    mock_hold_policy_service: Mock,
    mock_patron_barring_service: Mock,
    mock_loan_policy_service: Mock,
) -> HoldService:
    return HoldService(
        hold_repository=mock_hold_repository,
        patron_repository=mock_patron_repository,
        item_repository=mock_item_repository,
        copy_repository=mock_copy_repository,
        loan_repository=mock_loan_repository,
        staff_repository=mock_staff_repository,
        branch_repository=mock_branch_repository,
        patron_holding_service=mock_patron_holding_service,
        hold_policy_service=mock_hold_policy_service,
        patron_barring_service=mock_patron_barring_service,
        loan_policy_service=mock_loan_policy_service,
    )


def test_loan_service_find_all_loans(loan_service: LoanService, mock_loan_repository: Mock) -> None:
    loans = [Mock(spec=Loan), Mock(spec=Loan)]
    mock_loan_repository.find_all.return_value = loans

    result = loan_service.find_all_loans()

    assert result == loans


def test_loan_service_get_loan_success(loan_service: LoanService, mock_loan_repository: Mock) -> None:
    loan = Mock(spec=Loan, id='loan-123')
    mock_loan_repository.get_by_id.return_value = loan

    result = loan_service.get_loan('loan-123')

    assert result == loan


def test_loan_service_get_loan_not_found(loan_service: LoanService, mock_loan_repository: Mock) -> None:
    mock_loan_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Loan with id loan-999 not found'):
        loan_service.get_loan('loan-999')


def test_loan_service_checkout_copy(
    loan_service: LoanService,
    mock_loan_repository: Mock,
    mock_patron_repository: Mock,
    mock_staff_repository: Mock,
    mock_branch_repository: Mock,
    mock_copy_repository: Mock,
) -> None:
    patron = Mock(spec=Patron, id='patron-123', branch_id='branch-456')
    staff = Mock(spec=Staff, id='staff-789')
    branch = Mock(spec=Branch, id='branch-456')
    copy = Mock(spec=Copy, id='copy-101')
    loan = Mock(spec=Loan)

    mock_patron_repository.get_by_id.return_value = patron
    mock_staff_repository.get_by_id.return_value = staff
    mock_branch_repository.get_by_id.return_value = branch
    mock_copy_repository.get_by_id.return_value = copy
    mock_loan_repository.save.return_value = loan

    result = loan_service.checkout_copy(copy_id='copy-101', patron_id='patron-123', staff_out_id='staff-789')

    assert result == loan
    mock_loan_repository.save.assert_called_once()


def test_loan_service_checkout_patron_not_found(loan_service: LoanService, mock_patron_repository: Mock) -> None:
    mock_patron_repository.get_by_id.return_value = None

    with pytest.raises(PatronNotFoundError):
        loan_service.checkout_copy(copy_id='copy-1', patron_id='patron-999', staff_out_id='staff-1')


def test_loan_service_checkin_copy(
    loan_service: LoanService, mock_loan_repository: Mock, mock_copy_repository: Mock
) -> None:
    loan = Mock(spec=Loan, id='loan-123', copy_id='copy-456')
    copy = Mock(spec=Copy, id='copy-456')

    mock_loan_repository.get_by_id.return_value = loan
    mock_copy_repository.get_by_id.return_value = copy
    mock_loan_repository.save.return_value = loan

    result = loan_service.checkin_copy(loan_id='loan-123', staff_in_id='staff-789')

    assert result == loan
    loan.mark_as_returned.assert_called_once()


def test_loan_service_damaged_copy(
    loan_service: LoanService, mock_loan_repository: Mock, mock_copy_repository: Mock
) -> None:
    loan = Mock(spec=Loan, id='loan-123', copy_id='copy-456')
    copy = Mock(spec=Copy, id='copy-456')

    mock_loan_repository.get_by_id.return_value = loan
    mock_copy_repository.get_by_id.return_value = copy
    mock_loan_repository.save.return_value = loan

    result = loan_service.damaged_copy(loan_id='loan-123')

    assert result == loan
    loan.mark_damaged.assert_called_once()


def test_loan_service_lost_copy(
    loan_service: LoanService, mock_loan_repository: Mock, mock_copy_repository: Mock
) -> None:
    loan = Mock(spec=Loan, id='loan-123', copy_id='copy-456')
    copy = Mock(spec=Copy, id='copy-456')

    mock_loan_repository.get_by_id.return_value = loan
    mock_copy_repository.get_by_id.return_value = copy
    mock_loan_repository.save.return_value = loan

    result = loan_service.lost_copy(loan_id='loan-123')

    assert result == loan
    loan.mark_lost.assert_called_once()


def test_loan_service_renew_loan(
    loan_service: LoanService, mock_loan_repository: Mock, mock_patron_repository: Mock, mock_copy_repository: Mock
) -> None:
    loan = Mock(spec=Loan, id='loan-123', patron_id='patron-456', copy_id='copy-789')
    patron = Mock(spec=Patron, id='patron-456')
    copy = Mock(spec=Copy, id='copy-789')

    mock_loan_repository.get_by_id.return_value = loan
    mock_patron_repository.get_by_id.return_value = patron
    mock_copy_repository.get_by_id.return_value = copy
    mock_loan_repository.save.return_value = loan

    result = loan_service.renew_loan(loan_id='loan-123')

    assert result == loan
    loan.renew.assert_called_once()


def test_hold_service_find_all_holds(hold_service: HoldService, mock_hold_repository: Mock) -> None:
    holds = [Mock(spec=Hold), Mock(spec=Hold)]
    mock_hold_repository.find_all.return_value = holds

    result = hold_service.find_all_holds()

    assert result == holds
