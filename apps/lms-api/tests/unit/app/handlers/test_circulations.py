from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

from flask import Flask

from lms.app.handlers.circulations import register_handler, handle_loan_returned
from lms.domain.circulations.events import LoanReturnedEvent


def test_handle_loan_returned_processes_holds(app: Flask) -> None:
    mock_hold_service = MagicMock()

    # Inject mocks into container
    mock_container = MagicMock()
    mock_container.hold_service = mock_hold_service
    app.container = mock_container  # type: ignore

    copy_id = str(uuid.uuid4())
    event = LoanReturnedEvent(
        loan_id=str(uuid.uuid4()),
        copy_id=copy_id,
        patron_id=str(uuid.uuid4()),
        branch_id=str(uuid.uuid4()),
        staff_in_id=str(uuid.uuid4()),
        loan_date=None,  # type: ignore
        due_date=None,  # type: ignore
        return_date=None,  # type: ignore
    )

    handle_loan_returned(event)

    mock_hold_service.process_holds_for_returned_copy.assert_called_once_with(copy_id=copy_id)


def test_handle_loan_returned_with_different_copy_ids(app: Flask) -> None:
    mock_hold_service = MagicMock()

    # Inject mocks into container
    mock_container = MagicMock()
    mock_container.hold_service = mock_hold_service
    app.container = mock_container  # type: ignore

    copy_id_1 = str(uuid.uuid4())
    copy_id_2 = str(uuid.uuid4())

    event_1 = LoanReturnedEvent(
        loan_id=str(uuid.uuid4()),
        copy_id=copy_id_1,
        patron_id=str(uuid.uuid4()),
        branch_id=str(uuid.uuid4()),
        staff_in_id=str(uuid.uuid4()),
        loan_date=None,  # type: ignore
        due_date=None,  # type: ignore
        return_date=None,  # type: ignore
    )

    event_2 = LoanReturnedEvent(
        loan_id=str(uuid.uuid4()),
        copy_id=copy_id_2,
        patron_id=str(uuid.uuid4()),
        branch_id=str(uuid.uuid4()),
        staff_in_id=str(uuid.uuid4()),
        loan_date=None,  # type: ignore
        due_date=None,  # type: ignore
        return_date=None,  # type: ignore
    )

    handle_loan_returned(event_1)
    handle_loan_returned(event_2)

    assert mock_hold_service.process_holds_for_returned_copy.call_count == 2
    calls = mock_hold_service.process_holds_for_returned_copy.call_args_list
    assert calls[0].kwargs['copy_id'] == copy_id_1
    assert calls[1].kwargs['copy_id'] == copy_id_2


@patch('lms.app.handlers.circulations.event_bus')
def test_register_handler_subscribes_to_event(mock_event_bus: MagicMock, app: Flask) -> None:
    register_handler(app)

    mock_event_bus.subscribe.assert_called_once_with(LoanReturnedEvent, handle_loan_returned)


def test_handle_loan_returned_called_once_per_event(app: Flask) -> None:
    mock_hold_service = MagicMock()

    # Inject mocks into container
    mock_container = MagicMock()
    mock_container.hold_service = mock_hold_service
    app.container = mock_container  # type: ignore

    event = LoanReturnedEvent(
        loan_id=str(uuid.uuid4()),
        copy_id=str(uuid.uuid4()),
        patron_id=str(uuid.uuid4()),
        branch_id=str(uuid.uuid4()),
        staff_in_id=str(uuid.uuid4()),
        loan_date=None,  # type: ignore
        due_date=None,  # type: ignore
        return_date=None,  # type: ignore
    )

    handle_loan_returned(event)

    # Verify service method called exactly once
    assert mock_hold_service.process_holds_for_returned_copy.call_count == 1
