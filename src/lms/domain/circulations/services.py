from __future__ import annotations

from datetime import date, timedelta

from lms.domain.patrons.entities import Patron
from lms.domain.catalogs.entities import Copy
from lms.domain.circulations.repositories import HoldRepository


class LoanPolicyService:
    def calculate_due_date(self, loan_date: date, patron: Patron, copy: Copy) -> date:
        if patron.is_premium_membership() or copy.is_older_version():
            return loan_date + timedelta(days=28)
        return loan_date + timedelta(days=14)

    def calculate_new_due_date(self, patron: Patron, copy: Copy) -> date:
        return self.calculate_due_date(loan_date=date.today(), patron=patron, copy=copy)


class HoldPolicyService:
    def __init__(self, /, *, hold_repository: HoldRepository) -> None:
        self.hold_repository = hold_repository

    def calculate_hold_expiry_date(self, request_date: date) -> date:
        return request_date + timedelta(days=7)

    def is_hold_expired(self, hold_request_date: date) -> bool:
        current_date = date.today()
        expiry_date = self.calculate_hold_expiry_date(hold_request_date)
        return current_date > expiry_date
