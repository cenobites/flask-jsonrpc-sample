from __future__ import annotations

from decimal import Decimal
import datetime
from unittest.mock import Mock, patch
from collections.abc import Iterator

import pytest

from lms.domain.patrons.entities import Fine, Patron
from lms.domain.patrons.exceptions import (
    FineAlreadyPaid,
    PatronNotActive,
    PatronNotArchived,
    FineAAlreadyWaived,
    PatronNotSuspended,
    PatronAlreadyActive,
    PatronHasActiveLoans,
    PatronEmailAlreadyExists,
)
from lms.infrastructure.database.models.patrons import FineStatus, PatronStatus


@pytest.fixture
def mock_event_bus() -> Iterator:
    with patch('lms.domain.patrons.entities.event_bus') as mock_bus:
        yield mock_bus


@pytest.fixture
def mock_patron_uniqueness_service() -> Iterator:
    service = Mock()
    service.is_email_unique.return_value = True
    return service


@pytest.fixture
def mock_patron_barring_service() -> Iterator:
    service = Mock()
    service.can_borrow_copies.return_value = True
    service.can_renew_copy.return_value = True
    return service


@pytest.fixture
def mock_patron_holding_service() -> Iterator:
    service = Mock()
    service.can_place_holds.return_value = True
    return service


@pytest.fixture
def mock_patron_reinstatement_service() -> Iterator:
    service = Mock()
    service.can_reinstate.return_value = True
    return service


@pytest.fixture
def mock_fine_policy_service() -> Iterator:
    service = Mock()
    service.calculate_overdue_fine.return_value = Decimal('5.00')
    service.calculate_fine_for_damaged_item.return_value = Decimal('25.00')
    service.calculate_fine_for_lost_item.return_value = Decimal('50.00')
    return service


class TestPatron:
    def test_create_patron(self, mock_event_bus: object, mock_patron_uniqueness_service: object) -> None:
        patron = Patron.create(
            name='John Doe',
            email='john@example.com',
            branch_id='branch1',
            patron_uniqueness_service=mock_patron_uniqueness_service,
        )

        assert patron.name == 'John Doe'
        assert patron.email == 'john@example.com'
        assert patron.branch_id == 'branch1'
        assert patron.status == PatronStatus.REGISTERED.value
        assert patron.member_since == datetime.date.today()
        mock_event_bus.add_event.assert_called_once()

    def test_create_patron_duplicate_email(
        self, mock_event_bus: object, mock_patron_uniqueness_service: object
    ) -> None:
        mock_patron_uniqueness_service.is_email_unique.return_value = False

        with pytest.raises(PatronEmailAlreadyExists):
            Patron.create(
                name='Jane Doe',
                email='duplicate@example.com',
                branch_id='branch1',
                patron_uniqueness_service=mock_patron_uniqueness_service,
            )

    def test_is_premium_membership(self, mock_event_bus: object) -> None:
        old_date = datetime.date.today() - datetime.timedelta(days=365 * 6)
        patron = Patron(
            id='p1', name='Premium Member', email='premium@example.com', branch_id='branch1', member_since=old_date
        )

        assert patron.is_premium_membership() is True

    def test_is_not_premium_membership(self, mock_event_bus: object) -> None:
        recent_date = datetime.date.today() - datetime.timedelta(days=365 * 3)
        patron = Patron(
            id='p1', name='Regular Member', email='regular@example.com', branch_id='branch1', member_since=recent_date
        )

        assert patron.is_premium_membership() is False

    def test_change_email(self, mock_event_bus: object, mock_patron_uniqueness_service: object) -> None:
        patron = Patron(id='p1', name='Test Patron', email='old@example.com', branch_id='branch1')

        patron.change_email('new@example.com', mock_patron_uniqueness_service)

        assert patron.email == 'new@example.com'
        mock_event_bus.add_event.assert_called_once()

    def test_change_email_same(self, mock_event_bus: object, mock_patron_uniqueness_service: object) -> None:
        patron = Patron(id='p1', name='Test Patron', email='same@example.com', branch_id='branch1')

        patron.change_email('same@example.com', mock_patron_uniqueness_service)

        assert patron.email == 'same@example.com'
        mock_event_bus.add_event.assert_not_called()

    def test_change_email_duplicate(self, mock_event_bus: object, mock_patron_uniqueness_service: object) -> None:
        patron = Patron(id='p1', name='Test Patron', email='old@example.com', branch_id='branch1')
        mock_patron_uniqueness_service.is_email_unique.return_value = False

        with pytest.raises(PatronEmailAlreadyExists):
            patron.change_email('duplicate@example.com', mock_patron_uniqueness_service)

    def test_available_to_borrow(self, mock_event_bus: object, mock_patron_barring_service: object) -> None:
        patron = Patron(
            id='p1', name='Test Patron', email='test@example.com', branch_id='branch1', status=PatronStatus.ACTIVE.value
        )

        patron.available_to_borrow(mock_patron_barring_service)

    def test_available_to_borrow_not_active(self, mock_event_bus: object, mock_patron_barring_service: object) -> None:
        patron = Patron(
            id='p1',
            name='Test Patron',
            email='test@example.com',
            branch_id='branch1',
            status=PatronStatus.SUSPENDED.value,
        )

        with pytest.raises(PatronNotActive):
            patron.available_to_borrow(mock_patron_barring_service)

    def test_available_to_borrow_has_active_loans(
        self, mock_event_bus: object, mock_patron_barring_service: object
    ) -> None:
        patron = Patron(
            id='p1', name='Test Patron', email='test@example.com', branch_id='branch1', status=PatronStatus.ACTIVE.value
        )
        mock_patron_barring_service.can_borrow_copies.return_value = False

        with pytest.raises(PatronHasActiveLoans):
            patron.available_to_borrow(mock_patron_barring_service)

    def test_available_to_renew(self, mock_event_bus: object, mock_patron_barring_service: object) -> None:
        patron = Patron(
            id='p1', name='Test Patron', email='test@example.com', branch_id='branch1', status=PatronStatus.ACTIVE.value
        )

        patron.available_to_renew('copy1', mock_patron_barring_service)

    def test_available_to_place_hold(self, mock_event_bus: object, mock_patron_holding_service: object) -> None:
        patron = Patron(
            id='p1', name='Test Patron', email='test@example.com', branch_id='branch1', status=PatronStatus.ACTIVE.value
        )

        patron.available_to_place_hold(mock_patron_holding_service)

    def test_activate_patron(self, mock_event_bus: object) -> None:
        patron = Patron(
            id='p1',
            name='Test Patron',
            email='test@example.com',
            branch_id='branch1',
            status=PatronStatus.REGISTERED.value,
        )

        patron.activate()

        assert patron.status == PatronStatus.ACTIVE.value

    def test_activate_already_active_patron(self, mock_event_bus: object) -> None:
        patron = Patron(
            id='p1', name='Test Patron', email='test@example.com', branch_id='branch1', status=PatronStatus.ACTIVE.value
        )

        with pytest.raises(PatronAlreadyActive):
            patron.activate()

    def test_archive_patron(self, mock_event_bus: object) -> None:
        patron = Patron(
            id='p1', name='Test Patron', email='test@example.com', branch_id='branch1', status=PatronStatus.ACTIVE.value
        )

        patron.archive()

        assert patron.status == PatronStatus.ARCHIVED.value

    def test_unarchive_patron(self, mock_event_bus: object) -> None:
        patron = Patron(
            id='p1',
            name='Test Patron',
            email='test@example.com',
            branch_id='branch1',
            status=PatronStatus.ARCHIVED.value,
        )

        patron.unarchive()

        assert patron.status == PatronStatus.ACTIVE.value

    def test_unarchive_not_archived_patron(self, mock_event_bus: object) -> None:
        patron = Patron(
            id='p1', name='Test Patron', email='test@example.com', branch_id='branch1', status=PatronStatus.ACTIVE.value
        )

        with pytest.raises(PatronNotArchived):
            patron.unarchive()

    def test_reinstate_patron(self, mock_event_bus: object, mock_patron_reinstatement_service: object) -> None:
        patron = Patron(
            id='p1',
            name='Test Patron',
            email='test@example.com',
            branch_id='branch1',
            status=PatronStatus.SUSPENDED.value,
        )

        patron.reinstate(mock_patron_reinstatement_service)

        assert patron.status == PatronStatus.ACTIVE.value
        mock_event_bus.add_event.assert_called_once()

    def test_reinstate_not_suspended_patron(
        self, mock_event_bus: object, mock_patron_reinstatement_service: object
    ) -> None:
        patron = Patron(
            id='p1', name='Test Patron', email='test@example.com', branch_id='branch1', status=PatronStatus.ACTIVE.value
        )

        with pytest.raises(PatronNotSuspended):
            patron.reinstate(mock_patron_reinstatement_service)


class TestFine:
    def test_create_for_overdue(self, mock_event_bus: object, mock_fine_policy_service: object) -> None:
        fine = Fine.create_for_overdue(
            loan_id='loan1', patron_id='patron1', days_late=5, fine_policy_service=mock_fine_policy_service
        )

        assert fine.loan_id == 'loan1'
        assert fine.patron_id == 'patron1'
        assert fine.amount == Decimal('5.00')
        assert fine.status == FineStatus.UNPAID.value
        assert 'Overdue fine' in fine.reason
        mock_event_bus.add_event.assert_called_once()

    def test_create_for_damaged_item(self, mock_event_bus: object, mock_fine_policy_service: object) -> None:
        fine = Fine.create_for_damaged_item(
            loan_id='loan1', patron_id='patron1', copy_id='copy1', fine_policy_service=mock_fine_policy_service
        )

        assert fine.loan_id == 'loan1'
        assert fine.patron_id == 'patron1'
        assert fine.amount == Decimal('25.00')
        assert fine.status == FineStatus.UNPAID.value
        assert 'Damaged fine' in fine.reason

    def test_create_for_lost_item(self, mock_event_bus: object, mock_fine_policy_service: object) -> None:
        fine = Fine.create_for_lost_item(
            loan_id='loan1', patron_id='patron1', copy_id='copy1', fine_policy_service=mock_fine_policy_service
        )

        assert fine.loan_id == 'loan1'
        assert fine.patron_id == 'patron1'
        assert fine.amount == Decimal('50.00')
        assert fine.status == FineStatus.UNPAID.value
        assert 'Lost fine' in fine.reason

    def test_pay_fine(self, mock_event_bus: object) -> None:
        fine = Fine(
            id='fine1', patron_id='patron1', loan_id='loan1', amount=Decimal('10.00'), status=FineStatus.UNPAID.value
        )

        fine.pay()

        assert fine.status == FineStatus.PAID.value
        assert fine.paid_date == datetime.date.today()

    def test_pay_already_paid_fine(self, mock_event_bus: object) -> None:
        fine = Fine(
            id='fine1',
            patron_id='patron1',
            loan_id='loan1',
            amount=Decimal('10.00'),
            status=FineStatus.PAID.value,
            paid_date=datetime.date.today(),
        )

        with pytest.raises(FineAlreadyPaid):
            fine.pay()

    def test_waive_fine(self, mock_event_bus: object) -> None:
        fine = Fine(
            id='fine1', patron_id='patron1', loan_id='loan1', amount=Decimal('10.00'), status=FineStatus.UNPAID.value
        )

        fine.waive()

        assert fine.status == FineStatus.WAIVED.value
        assert fine.paid_date == datetime.date.today()

    def test_waive_already_waived_fine(self, mock_event_bus: object) -> None:
        fine = Fine(
            id='fine1',
            patron_id='patron1',
            loan_id='loan1',
            amount=Decimal('10.00'),
            status=FineStatus.WAIVED.value,
            paid_date=datetime.date.today(),
        )

        with pytest.raises(FineAAlreadyWaived):
            fine.waive()
