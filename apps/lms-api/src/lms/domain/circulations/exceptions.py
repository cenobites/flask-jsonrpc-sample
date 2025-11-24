from __future__ import annotations

from datetime import date

from lms.domain import DomainError


class LoanAlreadyReturned(DomainError):
    def __init__(self, loan_id: str, return_date: date, /) -> None:
        super().__init__(f'Loan {loan_id} is already returned at {return_date!r}')
        self.loan_id = loan_id
        self.return_date = return_date


class LoanOverdue(DomainError):
    def __init__(self, loan_id: str, days_late: int, /) -> None:
        super().__init__(f'Loan {loan_id} is overdue by {days_late} days')
        self.loan_id = loan_id
        self.days_late = days_late


class HoldNotPending(DomainError):
    def __init__(self, hold_id: str, /) -> None:
        super().__init__(f'Hold {hold_id} is not pending')
        self.hold_id = hold_id
