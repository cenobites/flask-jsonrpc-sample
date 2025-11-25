from __future__ import annotations

from decimal import Decimal

from lms.domain import DomainNotFound
from lms.domain.catalogs.repositories import CopyRepository, ItemRepository
from lms.domain.circulations.repositories import HoldRepository, LoanRepository
from lms.infrastructure.database.models.patrons import PatronStatus
from lms.infrastructure.database.models.catalogs import ItemFormat

from .repositories import PatronRepository


class PatronUniquenessService:
    def __init__(self, /, *, patron_repository: PatronRepository) -> None:
        self.patron_repository = patron_repository

    def is_email_unique(self, email: str) -> bool:
        return not self.patron_repository.exists_by_email(email)


class PatronBarringService:
    def __init__(self, /, *, patron_repository: PatronRepository, loan_repository: LoanRepository) -> None:
        self.patron_repository = patron_repository
        self.loan_repository = loan_repository

    def can_borrow_copies(self, patron_id: str) -> bool:
        patron = self.patron_repository.get_by_id(patron_id)
        if patron is None:
            return False
        loans = self.loan_repository.find_by_patron_id(patron_id)
        return patron.status == PatronStatus.ACTIVE.value and len(loans) == 0

    def can_renew_copy(self, patron_id: str, copy_id: str) -> bool:
        patron = self.patron_repository.get_by_id(patron_id)
        if patron is None:
            return False
        loans = self.loan_repository.find_by_patron_id(patron_id)
        loan = next((loan for loan in loans if loan.copy_id == copy_id), None)
        if loan is None:
            return False
        return patron.status == PatronStatus.ACTIVE.value and len(loans) == 1


class PatronHoldingService:
    def __init__(self, /, *, hold_repository: HoldRepository) -> None:
        self.hold_repository = hold_repository

    def can_place_holds(self, patron_id: str) -> bool:
        pending_holds = self.hold_repository.find_active_holds_by_patron(patron_id=patron_id)
        return len(pending_holds) <= 1


class PatronReinstatementService:
    def __init__(self, /, *, patron_repository: PatronRepository, loan_repository: LoanRepository) -> None:
        self.patron_repository = patron_repository
        self.loan_repository = loan_repository

    def can_reinstate(self, patron_id: str) -> bool:
        patron = self.patron_repository.get_by_id(patron_id)
        if patron is None:
            return False
        loans = self.loan_repository.find_by_patron_id(patron_id)
        return patron.status == PatronStatus.SUSPENDED.value and len(loans) == 0


class FinePolicyService:
    def __init__(self, /, *, copy_repository: CopyRepository, item_repository: ItemRepository) -> None:
        self.processing_fee = 10.0
        self.damage_fee = {
            ItemFormat.BOOK.value: 20.0,
            ItemFormat.EBOOK.value: 1.0,
            ItemFormat.DVD.value: 25.0,
            ItemFormat.CD.value: 15.0,
            ItemFormat.MAGAZINE.value: 15.0,
            'default': 10.0,
        }
        self.replacement_cost = {
            ItemFormat.BOOK.value: 50.0,
            ItemFormat.EBOOK.value: 15.0,
            ItemFormat.DVD.value: 35.0,
            ItemFormat.CD.value: 35.0,
            ItemFormat.MAGAZINE.value: 25.0,
            'default': 50.0,
        }
        self.copy_repository = copy_repository
        self.item_repository = item_repository

    def calculate_overdue_fine(self, days_late: int) -> Decimal:
        daily_rate = 0.5
        return Decimal(days_late) * Decimal(daily_rate)

    def calculate_fine_for_damaged_item(self, copy_id: str) -> Decimal:
        copy = self.copy_repository.get_by_id(copy_id)
        if not copy:
            raise DomainNotFound('Copy', copy_id)
        item = self.item_repository.get_by_id(copy.item_id)
        if not item:
            raise DomainNotFound('Item', copy.item_id)
        return Decimal(self.damage_fee.get(item.format, self.damage_fee['default']) + self.processing_fee)

    def calculate_fine_for_lost_item(self, copy_id: str) -> Decimal:
        copy = self.copy_repository.get_by_id(copy_id)
        if not copy:
            raise DomainNotFound('Copy', copy_id)
        item = self.item_repository.get_by_id(copy.item_id)
        if not item:
            raise DomainNotFound('Item', copy.item_id)
        return Decimal(self.replacement_cost.get(item.format, self.replacement_cost['default']) + self.processing_fee)
