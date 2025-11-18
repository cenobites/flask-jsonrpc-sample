from __future__ import annotations

from flask import Flask, current_app

from lms.infrastructure.logging import logger
from lms.infrastructure.event_bus import event_bus
from lms.app.services.organization import StaffService
from lms.domain.organization.events import BranchClosedEvent, BranchOpenedEvent, ManagerAssignedToBranchEvent


def handle_branch_opened(event: BranchOpenedEvent) -> None:
    logger.info('Branch opened: ID=%s, Name=%s', event.branch_id, event.branch_name)


def handle_branch_closed(event: BranchClosedEvent) -> None:
    logger.info('Branch closed: ID=%s', event.branch_id)


def handle_manager_assigned_to_branch(event: ManagerAssignedToBranchEvent) -> None:
    logger.info('Manager assigned to branch: ManagerID=%s, BranchID=%s', event.manager_id, event.branch_id)
    staff_service: StaffService = current_app.container.staff_service()  # type: ignore
    staff_service.assign_staff_to_branch(event.manager_id, event.branch_id)
    logger.info('Manager with ID=%s assigned to BranchID=%s successfully', event.manager_id, event.branch_id)


def register_handler(app: Flask) -> None:
    event_bus.subscribe(BranchOpenedEvent, handle_branch_opened)
    event_bus.subscribe(BranchClosedEvent, handle_branch_closed)
    event_bus.subscribe(ManagerAssignedToBranchEvent, handle_manager_assigned_to_branch)
