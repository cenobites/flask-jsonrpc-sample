from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

from flask import Flask

from lms.app.handlers.organizations import (
    register_handler,
    handle_branch_closed,
    handle_branch_opened,
    handle_manager_assigned_to_branch,
)
from lms.domain.organizations.events import BranchClosedEvent, BranchOpenedEvent, ManagerAssignedToBranchEvent


def test_handle_branch_opened_logs_event(app: Flask) -> None:
    branch_id = str(uuid.uuid4())
    branch_name = 'Downtown Library'
    event = BranchOpenedEvent(branch_id=branch_id, branch_name=branch_name)

    # Should not raise any exception
    handle_branch_opened(event)


def test_handle_branch_opened_with_different_names(app: Flask) -> None:
    test_cases = [
        ('Main Branch', str(uuid.uuid4())),
        ('East Side Library', str(uuid.uuid4())),
        ('Community Center', str(uuid.uuid4())),
    ]

    for branch_name, branch_id in test_cases:
        event = BranchOpenedEvent(branch_id=branch_id, branch_name=branch_name)
        handle_branch_opened(event)


def test_handle_branch_closed_logs_event(app: Flask) -> None:
    branch_id = str(uuid.uuid4())
    event = BranchClosedEvent(branch_id=branch_id)

    # Should not raise any exception
    handle_branch_closed(event)


def test_handle_branch_closed_multiple_times(app: Flask) -> None:
    for _ in range(3):
        branch_id = str(uuid.uuid4())
        event = BranchClosedEvent(branch_id=branch_id)
        handle_branch_closed(event)


def test_handle_manager_assigned_to_branch_assigns_staff(app: Flask) -> None:
    mock_staff_service = MagicMock()
    app.container.staff_service = lambda: mock_staff_service  # type: ignore

    manager_id = str(uuid.uuid4())
    branch_id = str(uuid.uuid4())
    event = ManagerAssignedToBranchEvent(manager_id=manager_id, branch_id=branch_id)

    handle_manager_assigned_to_branch(event)

    mock_staff_service.assign_staff_to_branch.assert_called_once_with(manager_id, branch_id)


def test_handle_manager_assigned_to_branch_multiple_assignments(app: Flask) -> None:
    mock_staff_service = MagicMock()
    app.container.staff_service = lambda: mock_staff_service  # type: ignore

    assignments = [
        (str(uuid.uuid4()), str(uuid.uuid4())),
        (str(uuid.uuid4()), str(uuid.uuid4())),
        (str(uuid.uuid4()), str(uuid.uuid4())),
    ]

    for manager_id, branch_id in assignments:
        event = ManagerAssignedToBranchEvent(manager_id=manager_id, branch_id=branch_id)
        handle_manager_assigned_to_branch(event)

    assert mock_staff_service.assign_staff_to_branch.call_count == 3

    calls = mock_staff_service.assign_staff_to_branch.call_args_list
    for i, (manager_id, branch_id) in enumerate(assignments):
        assert calls[i].args == (manager_id, branch_id)


@patch('lms.app.handlers.organizations.event_bus')
def test_register_handler_subscribes_to_all_events(mock_event_bus: MagicMock, app: Flask) -> None:
    register_handler(app)

    assert mock_event_bus.subscribe.call_count == 3

    calls = mock_event_bus.subscribe.call_args_list

    # Verify BranchOpenedEvent subscription
    assert calls[0].args == (BranchOpenedEvent, handle_branch_opened)

    # Verify BranchClosedEvent subscription
    assert calls[1].args == (BranchClosedEvent, handle_branch_closed)

    # Verify ManagerAssignedToBranchEvent subscription
    assert calls[2].args == (ManagerAssignedToBranchEvent, handle_manager_assigned_to_branch)


def test_handle_manager_assigned_same_manager_different_branches(app: Flask) -> None:
    mock_staff_service = MagicMock()
    app.container.staff_service = lambda: mock_staff_service  # type: ignore

    manager_id = str(uuid.uuid4())
    branch_id_1 = str(uuid.uuid4())
    branch_id_2 = str(uuid.uuid4())

    event_1 = ManagerAssignedToBranchEvent(manager_id=manager_id, branch_id=branch_id_1)
    event_2 = ManagerAssignedToBranchEvent(manager_id=manager_id, branch_id=branch_id_2)

    handle_manager_assigned_to_branch(event_1)
    handle_manager_assigned_to_branch(event_2)

    calls = mock_staff_service.assign_staff_to_branch.call_args_list
    assert calls[0].args == (manager_id, branch_id_1)
    assert calls[1].args == (manager_id, branch_id_2)


def test_handle_manager_assigned_different_managers_same_branch(app: Flask) -> None:
    mock_staff_service = MagicMock()
    app.container.staff_service = lambda: mock_staff_service  # type: ignore

    manager_id_1 = str(uuid.uuid4())
    manager_id_2 = str(uuid.uuid4())
    branch_id = str(uuid.uuid4())

    event_1 = ManagerAssignedToBranchEvent(manager_id=manager_id_1, branch_id=branch_id)
    event_2 = ManagerAssignedToBranchEvent(manager_id=manager_id_2, branch_id=branch_id)

    handle_manager_assigned_to_branch(event_1)
    handle_manager_assigned_to_branch(event_2)

    calls = mock_staff_service.assign_staff_to_branch.call_args_list
    assert calls[0].args == (manager_id_1, branch_id)
    assert calls[1].args == (manager_id_2, branch_id)
