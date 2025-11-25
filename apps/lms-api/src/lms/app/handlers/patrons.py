from __future__ import annotations

from flask import Flask, current_app

from lms.app.services.patrons import FineService
from lms.infrastructure.logging import logger
from lms.infrastructure.event_bus import event_bus
from lms.domain.circulations.events import LoanDamagedEvent, LoanOverdueEvent, LoanMarkedLostEvent


def handle_loan_overdue(event: LoanOverdueEvent) -> None:
    logger.info('Loan overdue: Loan ID=%s, Patron ID=%s, Days Late=%s', event.loan_id, event.patron_id, event.days_late)
    fine_service: FineService = current_app.container.fine_service()  # type: ignore
    fine = fine_service.process_overdue_loan(
        loan_id=event.loan_id, patron_id=event.patron_id, days_late=event.days_late
    )
    logger.info(
        'Created overdue fine of amount %s for loan ID %s (patron ID %s)', fine.amount, event.loan_id, event.patron_id
    )


def handle_loan_marked_damaged(event: LoanDamagedEvent) -> None:
    logger.info(
        'Loan marked damaged: Loan ID=%s, Copy ID=%s, Patron ID=%s, Branch ID=%s',
        event.loan_id,
        event.copy_id,
        event.patron_id,
        event.branch_id,
    )


def handle_loan_marked_lost(event: LoanMarkedLostEvent) -> None:
    logger.info(
        'Loan marked lost: Loan ID=%s, Copy ID=%s, Patron ID=%s, Branch ID=%s',
        event.loan_id,
        event.copy_id,
        event.patron_id,
        event.branch_id,
    )


def register_handler(app: Flask) -> None:
    event_bus.subscribe(LoanOverdueEvent, handle_loan_overdue)
    event_bus.subscribe(LoanMarkedLostEvent, handle_loan_marked_lost)
    event_bus.subscribe(LoanDamagedEvent, handle_loan_marked_damaged)
