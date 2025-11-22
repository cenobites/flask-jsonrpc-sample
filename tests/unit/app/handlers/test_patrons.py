from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

from flask import Flask

from lms.app.handlers.patrons import (
    register_handler,
    handle_loan_overdue,
    handle_loan_marked_lost,
    handle_loan_marked_damaged,
)
from lms.domain.circulations.events import LoanDamagedEvent, LoanOverdueEvent, LoanMarkedLostEvent


def test_handle_loan_overdue_creates_fine(app: Flask) -> None:
    mock_fine_service = MagicMock()

    # Mock fine creation
    mock_fine = MagicMock()
    mock_fine.amount = Decimal('15.00')
    mock_fine_service.process_overdue_loan.return_value = mock_fine

    app.container.fine_service = lambda: mock_fine_service  # type: ignore

    loan_id = str(uuid.uuid4())
    patron_id = str(uuid.uuid4())
    days_late = 5

    event = LoanOverdueEvent(loan_id=loan_id, patron_id=patron_id, days_late=days_late)

    handle_loan_overdue(event)

    mock_fine_service.process_overdue_loan.assert_called_once_with(
        loan_id=loan_id, patron_id=patron_id, days_late=days_late
    )


def test_handle_loan_overdue_with_different_days_late(app: Flask) -> None:
    mock_fine_service = MagicMock()
    mock_fine = MagicMock()
    mock_fine.amount = Decimal('10.00')
    mock_fine_service.process_overdue_loan.return_value = mock_fine

    app.container.fine_service = lambda: mock_fine_service  # type: ignore

    test_cases = [1, 5, 10, 30, 90]

    for days_late in test_cases:
        event = LoanOverdueEvent(loan_id=str(uuid.uuid4()), patron_id=str(uuid.uuid4()), days_late=days_late)
        handle_loan_overdue(event)

    assert mock_fine_service.process_overdue_loan.call_count == len(test_cases)

    calls = mock_fine_service.process_overdue_loan.call_args_list
    for i, days_late in enumerate(test_cases):
        assert calls[i].kwargs['days_late'] == days_late


def test_handle_loan_overdue_returns_fine_with_amount(app: Flask) -> None:
    mock_fine_service = MagicMock()

    fine_amounts = [Decimal('5.00'), Decimal('15.50'), Decimal('25.00')]

    for amount in fine_amounts:
        mock_fine = MagicMock()
        mock_fine.amount = amount
        mock_fine_service.process_overdue_loan.return_value = mock_fine

        app.container.fine_service = lambda: mock_fine_service  # type: ignore

        event = LoanOverdueEvent(loan_id=str(uuid.uuid4()), patron_id=str(uuid.uuid4()), days_late=5)

        handle_loan_overdue(event)


def test_handle_loan_marked_damaged_logs_event(app: Flask) -> None:
    event = LoanDamagedEvent(
        loan_id=str(uuid.uuid4()), copy_id=str(uuid.uuid4()), patron_id=str(uuid.uuid4()), branch_id=str(uuid.uuid4())
    )

    # Should not raise any exception
    handle_loan_marked_damaged(event)


def test_handle_loan_marked_damaged_multiple_events(app: Flask) -> None:
    for _ in range(5):
        event = LoanDamagedEvent(
            loan_id=str(uuid.uuid4()),
            copy_id=str(uuid.uuid4()),
            patron_id=str(uuid.uuid4()),
            branch_id=str(uuid.uuid4()),
        )
        handle_loan_marked_damaged(event)


def test_handle_loan_marked_lost_logs_event(app: Flask) -> None:
    event = LoanMarkedLostEvent(
        loan_id=str(uuid.uuid4()), copy_id=str(uuid.uuid4()), patron_id=str(uuid.uuid4()), branch_id=str(uuid.uuid4())
    )

    # Should not raise any exception
    handle_loan_marked_lost(event)


def test_handle_loan_marked_lost_multiple_events(app: Flask) -> None:
    for _ in range(5):
        event = LoanMarkedLostEvent(
            loan_id=str(uuid.uuid4()),
            copy_id=str(uuid.uuid4()),
            patron_id=str(uuid.uuid4()),
            branch_id=str(uuid.uuid4()),
        )
        handle_loan_marked_lost(event)


@patch('lms.app.handlers.patrons.event_bus')
def test_register_handler_subscribes_to_all_events(mock_event_bus: MagicMock, app: Flask) -> None:
    register_handler(app)

    assert mock_event_bus.subscribe.call_count == 3

    calls = mock_event_bus.subscribe.call_args_list

    # Verify LoanOverdueEvent subscription
    assert calls[0].args == (LoanOverdueEvent, handle_loan_overdue)

    # Verify LoanMarkedLostEvent subscription
    assert calls[1].args == (LoanMarkedLostEvent, handle_loan_marked_lost)

    # Verify LoanDamagedEvent subscription
    assert calls[2].args == (LoanDamagedEvent, handle_loan_marked_damaged)


def test_handle_loan_overdue_with_zero_days_late(app: Flask) -> None:
    mock_fine_service = MagicMock()
    mock_fine = MagicMock()
    mock_fine.amount = Decimal('0.00')
    mock_fine_service.process_overdue_loan.return_value = mock_fine

    app.container.fine_service = lambda: mock_fine_service  # type: ignore

    event = LoanOverdueEvent(loan_id=str(uuid.uuid4()), patron_id=str(uuid.uuid4()), days_late=0)

    handle_loan_overdue(event)

    mock_fine_service.process_overdue_loan.assert_called_once_with(
        loan_id=event.loan_id, patron_id=event.patron_id, days_late=0
    )


def test_handle_loan_overdue_multiple_patrons(app: Flask) -> None:
    mock_fine_service = MagicMock()
    mock_fine = MagicMock()
    mock_fine.amount = Decimal('10.00')
    mock_fine_service.process_overdue_loan.return_value = mock_fine

    app.container.fine_service = lambda: mock_fine_service  # type: ignore

    patron_ids = [str(uuid.uuid4()) for _ in range(3)]

    for patron_id in patron_ids:
        event = LoanOverdueEvent(loan_id=str(uuid.uuid4()), patron_id=patron_id, days_late=7)
        handle_loan_overdue(event)

    assert mock_fine_service.process_overdue_loan.call_count == 3


def test_damaged_and_lost_events_with_same_ids(app: Flask) -> None:
    loan_id = str(uuid.uuid4())
    copy_id = str(uuid.uuid4())
    patron_id = str(uuid.uuid4())
    branch_id = str(uuid.uuid4())

    damaged_event = LoanDamagedEvent(loan_id=loan_id, copy_id=copy_id, patron_id=patron_id, branch_id=branch_id)

    lost_event = LoanMarkedLostEvent(loan_id=loan_id, copy_id=copy_id, patron_id=patron_id, branch_id=branch_id)

    # Both should execute without errors
    handle_loan_marked_damaged(damaged_event)
    handle_loan_marked_lost(lost_event)
