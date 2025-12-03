from __future__ import annotations

from flask import Flask, current_app

from lms.infrastructure.logging import logger
from lms.infrastructure.event_bus import event_bus
from lms.app.services.circulations import HoldService
from lms.domain.circulations.events import LoanReturnedEvent


def handle_loan_returned(event: LoanReturnedEvent) -> None:
    logger.info('Loan returned: ID=%s', event.loan_id)
    hold_service: HoldService = current_app.container.hold_service  # type: ignore
    hold_service.process_holds_for_returned_copy(copy_id=event.copy_id)


def register_handler(app: Flask) -> None:
    event_bus.subscribe(LoanReturnedEvent, handle_loan_returned)
