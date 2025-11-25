from __future__ import annotations

import typing as t
import datetime
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from collections.abc import Iterator

import pytest

from lms.domain.circulations.entities import Hold, Loan
from lms.domain.circulations.exceptions import LoanOverdue, HoldNotPending, LoanAlreadyReturned
from lms.infrastructure.database.models.circulations import HoldStatus


@pytest.fixture
def mock_event_bus() -> t.Generator[MagicMock | AsyncMock]:
    with patch('lms.domain.circulations.entities.event_bus') as mock_bus:
        yield mock_bus


@pytest.fixture
def mock_patron() -> Mock:
    patron = Mock()
    patron.id = 'patron1'
    patron.available_to_borrow = Mock()
    patron.available_to_renew = Mock()
    patron.available_to_place_hold = Mock()
    return patron


@pytest.fixture
def mock_copy() -> Mock:
    copy = Mock()
    copy.id = 'copy1'
    copy.mark_as_checked_out = Mock()
    copy.mark_as_available = Mock()
    copy.mark_as_damaged = Mock()
    copy.mark_as_lost = Mock()
    return copy


@pytest.fixture
def mock_item() -> Mock:
    item = Mock()
    item.id = 'item1'
    return item


@pytest.fixture
def mock_staff() -> Iterator:
    staff = Mock()
    staff.id = 'staff1'
    return staff


@pytest.fixture
def mock_branch() -> Mock:
    branch = Mock()
    branch.id = 'branch1'
    return branch


@pytest.fixture
def mock_patron_barring_service() -> Mock:
    service = Mock()
    return service


@pytest.fixture
def mock_loan_policy_service() -> Mock:
    service = Mock()
    service.calculate_due_date.return_value = datetime.date.today() + datetime.timedelta(days=14)
    service.calculate_new_due_date.return_value = datetime.date.today() + datetime.timedelta(days=14)
    return service


@pytest.fixture
def mock_patron_holding_service() -> Mock:
    service = Mock()
    return service


@pytest.fixture
def mock_hold_policy_service() -> Mock:
    service = Mock()
    service.calculate_hold_expiry_date.return_value = datetime.date.today() + datetime.timedelta(days=7)
    return service


class TestLoan:
    def test_create_loan(
        self,
        mock_event_bus: object,
        mock_copy: object,
        mock_patron: object,
        mock_staff: object,
        mock_branch: object,
        mock_patron_barring_service: object,
        mock_loan_policy_service: object,
    ) -> None:
        loan = Loan.create(
            copy=mock_copy,
            patron=mock_patron,
            staff=mock_staff,
            branch=mock_branch,
            patron_barring_service=mock_patron_barring_service,
            loan_policy_service=mock_loan_policy_service,
        )

        assert loan.copy_id == 'copy1'
        assert loan.patron_id == 'patron1'
        assert loan.branch_id == 'branch1'
        assert loan.staff_out_id == 'staff1'
        assert loan.loan_date == datetime.date.today()
        assert loan.return_date is None
        mock_copy.mark_as_checked_out.assert_called_once()
        mock_event_bus.add_event.assert_called_once()

    def test_mark_as_returned(self, mock_event_bus: object, mock_copy: object) -> None:
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=10),
            due_date=datetime.date.today() + datetime.timedelta(days=4),
        )
        return_date = datetime.date.today()

        loan.mark_as_returned(mock_copy, return_date, 'staff2')

        assert loan.return_date == return_date
        assert loan.staff_in_id == 'staff2'
        mock_copy.mark_as_available.assert_called_once()

    def test_mark_as_returned_overdue(self, mock_event_bus: object, mock_copy: object) -> None:
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=20),
            due_date=datetime.date.today() - datetime.timedelta(days=5),
        )
        return_date = datetime.date.today()

        loan.mark_as_returned(mock_copy, return_date, 'staff2')

        assert loan.return_date == return_date
        assert mock_event_bus.add_event.call_count == 2  # Return + Overdue events

    def test_mark_as_returned_already_returned(self, mock_event_bus: object, mock_copy: object) -> None:
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=10),
            due_date=datetime.date.today() + datetime.timedelta(days=4),
            return_date=datetime.date.today() - datetime.timedelta(days=1),
            staff_in_id='staff2',
        )

        with pytest.raises(LoanAlreadyReturned):
            loan.mark_as_returned(mock_copy, datetime.date.today(), 'staff3')

    def test_mark_damaged(self, mock_event_bus: object, mock_copy: object) -> None:
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=5),
            due_date=datetime.date.today() + datetime.timedelta(days=9),
        )

        loan.mark_damaged(mock_copy)

        assert loan.return_date == datetime.date.today()
        mock_copy.mark_as_damaged.assert_called_once()
        mock_event_bus.add_event.assert_called_once()

    def test_mark_damaged_overdue(self, mock_event_bus: object, mock_copy: object) -> None:
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=20),
            due_date=datetime.date.today() - datetime.timedelta(days=5),
        )

        with pytest.raises(LoanOverdue):
            loan.mark_damaged(mock_copy)

    def test_mark_lost(self, mock_event_bus: object, mock_copy: object) -> None:
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=5),
            due_date=datetime.date.today() + datetime.timedelta(days=9),
        )

        loan.mark_lost(mock_copy)

        assert loan.return_date == datetime.date.today()
        mock_copy.mark_as_lost.assert_called_once()
        mock_event_bus.add_event.assert_called_once()

    def test_mark_lost_overdue(self, mock_event_bus: object, mock_copy: object) -> None:
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=20),
            due_date=datetime.date.today() - datetime.timedelta(days=5),
        )

        with pytest.raises(LoanOverdue):
            loan.mark_lost(mock_copy)

    def test_renew(
        self,
        mock_event_bus: object,
        mock_patron: object,
        mock_copy: object,
        mock_patron_barring_service: object,
        mock_loan_policy_service: object,
    ) -> None:
        old_due_date = datetime.date.today() + datetime.timedelta(days=2)
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=12),
            due_date=old_due_date,
        )

        loan.renew(mock_patron, mock_copy, mock_patron_barring_service, mock_loan_policy_service)

        assert loan.due_date != old_due_date
        mock_patron.available_to_renew.assert_called_once()

    def test_renew_overdue_loan(
        self,
        mock_event_bus: object,
        mock_patron: object,
        mock_copy: object,
        mock_patron_barring_service: object,
        mock_loan_policy_service: object,
    ) -> None:
        loan = Loan(
            id='loan1',
            copy_id='copy1',
            patron_id='patron1',
            branch_id='branch1',
            staff_out_id='staff1',
            loan_date=datetime.date.today() - datetime.timedelta(days=20),
            due_date=datetime.date.today() - datetime.timedelta(days=5),
        )

        with pytest.raises(LoanOverdue):
            loan.renew(mock_patron, mock_copy, mock_patron_barring_service, mock_loan_policy_service)


class TestHold:
    def test_create_hold(
        self,
        mock_event_bus: object,
        mock_patron: object,
        mock_item: object,
        mock_patron_holding_service: object,
        mock_hold_policy_service: object,
    ) -> None:
        hold = Hold.create(
            patron=mock_patron,
            item=mock_item,
            copy=None,
            patron_holding_service=mock_patron_holding_service,
            hold_policy_service=mock_hold_policy_service,
        )

        assert hold.patron_id == 'patron1'
        assert hold.item_id == 'item1'
        assert hold.copy_id is None
        assert hold.status == HoldStatus.PENDING.value
        assert hold.request_date == datetime.date.today()
        assert hold.expiry_date is not None

    def test_create_hold_with_copy(
        self,
        mock_event_bus: object,
        mock_patron: object,
        mock_item: object,
        mock_copy: object,
        mock_patron_holding_service: object,
        mock_hold_policy_service: object,
    ) -> None:
        hold = Hold.create(
            patron=mock_patron,
            item=mock_item,
            copy=mock_copy,
            patron_holding_service=mock_patron_holding_service,
            hold_policy_service=mock_hold_policy_service,
        )

        assert hold.copy_id == 'copy1'

    def test_ready_for_pickup(self, mock_event_bus: object, mock_copy: object) -> None:
        hold = Hold(id='hold1', item_id='item1', patron_id='patron1', status=HoldStatus.PENDING.value)

        hold.ready_for_pickup(mock_copy)

        assert hold.status == HoldStatus.READY.value
        assert hold.copy_id == 'copy1'
        mock_event_bus.add_event.assert_called_once()

    def test_ready_for_pickup_not_pending(self, mock_event_bus: object, mock_copy: object) -> None:
        hold = Hold(id='hold1', item_id='item1', patron_id='patron1', status=HoldStatus.FULFILLED.value)

        with pytest.raises(HoldNotPending):
            hold.ready_for_pickup(mock_copy)

    def test_fulfill(self, mock_event_bus: object, mock_copy: object) -> None:
        mock_loan = Mock()
        mock_loan.id = 'loan1'
        hold = Hold(
            id='hold1',
            item_id='item1',
            patron_id='patron1',
            status=HoldStatus.PENDING.value,
            request_date=datetime.date.today(),
            expiry_date=datetime.date.today() + datetime.timedelta(days=7),
        )

        hold.fulfill(mock_copy, mock_loan)

        assert hold.status == HoldStatus.FULFILLED.value
        assert hold.copy_id == 'copy1'
        assert hold.loan_id == 'loan1'
        mock_event_bus.add_event.assert_called_once()

    def test_expire(self, mock_event_bus: object) -> None:
        hold = Hold(id='hold1', item_id='item1', patron_id='patron1', status=HoldStatus.PENDING.value)

        hold.expire()

        assert hold.status == HoldStatus.EXPIRED.value
        mock_event_bus.add_event.assert_called_once()

    def test_cancel(self, mock_event_bus: object) -> None:
        hold = Hold(id='hold1', item_id='item1', patron_id='patron1', status=HoldStatus.PENDING.value)

        hold.cancel()

        assert hold.status == HoldStatus.CANCELLED.value
        mock_event_bus.add_event.assert_called_once()

    def test_cancel_not_pending(self, mock_event_bus: object) -> None:
        hold = Hold(id='hold1', item_id='item1', patron_id='patron1', status=HoldStatus.FULFILLED.value)

        with pytest.raises(HoldNotPending):
            hold.cancel()
