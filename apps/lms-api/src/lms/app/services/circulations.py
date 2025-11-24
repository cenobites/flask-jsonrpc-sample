from __future__ import annotations

import typing as t
import datetime

from lms.app.exceptions.patrons import PatronNotFoundError
from lms.infrastructure.logging import logger
from lms.app.exceptions.catalogs import CopyNotFoundError, ItemNotFoundError
from lms.domain.patrons.entities import Patron
from lms.domain.patrons.services import PatronBarringService, PatronHoldingService
from lms.domain.catalogs.entities import Copy, Item
from lms.infrastructure.event_bus import event_bus
from lms.app.exceptions.circulations import HoldNotFoundError, LoanNotFoundError
from lms.domain.patrons.repositories import PatronRepository
from lms.app.exceptions.organizations import StaffNotFoundError, BranchNotFoundError
from lms.domain.catalogs.repositories import CopyRepository, ItemRepository
from lms.domain.circulations.entities import Hold, Loan
from lms.domain.circulations.services import HoldPolicyService, LoanPolicyService
from lms.domain.organizations.entities import Staff, Branch
from lms.domain.circulations.repositories import HoldRepository, LoanRepository
from lms.domain.organizations.repositories import StaffRepository, BranchRepository


class LoanService:
    def __init__(
        self,
        /,
        *,
        loan_repository: LoanRepository,
        patron_repository: PatronRepository,
        branch_repository: BranchRepository,
        staff_repository: StaffRepository,
        copy_repository: CopyRepository,
        loan_policy_service: LoanPolicyService,
        patron_barring_service: PatronBarringService,
    ) -> None:
        self.loan_repository = loan_repository
        self.patron_repository = patron_repository
        self.branch_repository = branch_repository
        self.staff_repository = staff_repository
        self.copy_repository = copy_repository
        self.loan_policy_service = loan_policy_service
        self.patron_barring_service = patron_barring_service

    def _get_copy(self, copy_id: str) -> Copy:
        copy = self.copy_repository.get_by_id(copy_id)
        if not copy:
            raise CopyNotFoundError(f'Copy with id {copy_id} not found')
        return copy

    def _get_patron(self, patron_id: str) -> Patron:
        patron = self.patron_repository.get_by_id(patron_id)
        if not patron:
            raise PatronNotFoundError(f'Patron with id {patron_id} not found')
        return patron

    def _get_staff(self, staff_id: str) -> Staff:
        staff = self.staff_repository.get_by_id(staff_id)
        if not staff:
            raise StaffNotFoundError(f'Staff with id {staff_id} not found')
        return staff

    def _get_branch(self, branch_id: str) -> Branch:
        branch = self.branch_repository.get_by_id(branch_id)
        if not branch:
            raise BranchNotFoundError(f'Branch with id {branch_id} not found')
        return branch

    def _get_loan(self, loan_id: str) -> Loan:
        loan = self.loan_repository.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundError(f'Loan with id {loan_id} not found')
        return loan

    def find_all_loans(self) -> list[Loan]:
        return self.loan_repository.find_all()

    def get_loan(self, loan_id: str) -> Loan:
        return self._get_loan(loan_id)

    def checkout_copy(self, copy_id: str, patron_id: str, staff_out_id: str) -> Loan:
        patron = self._get_patron(patron_id)
        staff = self._get_staff(staff_out_id)
        branch = self._get_branch(patron.branch_id)
        copy = self._get_copy(copy_id)
        loan = Loan.create(
            copy=copy,
            patron=patron,
            staff=staff,
            branch=branch,
            patron_barring_service=self.patron_barring_service,
            loan_policy_service=self.loan_policy_service,
        )
        created_loan = self.loan_repository.save(loan, copy)
        event_bus.publish_events()
        return created_loan

    def checkin_copy(self, loan_id: str, staff_in_id: str) -> Loan:
        loan = self._get_loan(loan_id)
        copy = self._get_copy(loan.copy_id)
        loan.mark_as_returned(copy=copy, return_date=datetime.date.today(), staff_in_id=staff_in_id)
        updated_loan = self.loan_repository.save(loan, copy)
        event_bus.publish_events()
        return updated_loan

    def damaged_copy(self, loan_id: str) -> Loan:
        loan = self._get_loan(loan_id)
        copy = self._get_copy(loan.copy_id)
        loan.mark_damaged(copy=copy)
        updated_loan = self.loan_repository.save(loan, copy)
        event_bus.publish_events()
        return updated_loan

    def lost_copy(self, loan_id: str) -> Loan:
        loan = self._get_loan(loan_id)
        copy = self._get_copy(loan.copy_id)
        loan.mark_lost(copy=copy)
        updated_loan = self.loan_repository.save(loan, copy)
        event_bus.publish_events()
        return updated_loan

    def renew_loan(self, loan_id: str) -> Loan:
        loan = self._get_loan(loan_id)
        patron = self._get_patron(loan.patron_id)
        copy = self._get_copy(loan.copy_id)
        loan.renew(
            patron=patron,
            copy=copy,
            patron_barring_service=self.patron_barring_service,
            loan_policy_service=self.loan_policy_service,
        )
        updated_loan = self.loan_repository.save(loan, copy)
        event_bus.publish_events()
        return updated_loan


class HoldService:
    def __init__(
        self,
        /,
        *,
        hold_repository: HoldRepository,
        patron_repository: PatronRepository,
        item_repository: ItemRepository,
        copy_repository: CopyRepository,
        loan_repository: LoanRepository,
        staff_repository: StaffRepository,
        branch_repository: BranchRepository,
        patron_holding_service: PatronHoldingService,
        hold_policy_service: HoldPolicyService,
        patron_barring_service: PatronBarringService,
        loan_policy_service: LoanPolicyService,
    ) -> None:
        self.hold_repository = hold_repository
        self.patron_repository = patron_repository
        self.item_repository = item_repository
        self.copy_repository = copy_repository
        self.loan_repository = loan_repository
        self.staff_repository = staff_repository
        self.branch_repository = branch_repository
        self.patron_holding_service = patron_holding_service
        self.hold_policy_service = hold_policy_service
        self.patron_barring_service = patron_barring_service
        self.loan_policy_service = loan_policy_service

    def _get_copy(self, copy_id: str) -> Copy:
        copy = self.copy_repository.get_by_id(copy_id)
        if not copy:
            raise CopyNotFoundError(f'Copy with id {copy_id} not found')
        return copy

    def _get_patron(self, patron_id: str) -> Patron:
        patron = self.patron_repository.get_by_id(patron_id)
        if not patron:
            raise PatronNotFoundError(f'Patron with id {patron_id} not found')
        return patron

    def _get_item(self, item_id: str) -> Item:
        item = self.item_repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(f'Item with id {item_id} not found')
        return item

    def _get_staff(self, staff_id: str) -> Staff:
        staff = self.staff_repository.get_by_id(staff_id)
        if not staff:
            raise StaffNotFoundError(f'Staff with id {staff_id} not found')
        return staff

    def _get_branch(self, branch_id: str) -> Branch:
        branch = self.branch_repository.get_by_id(branch_id)
        if not branch:
            raise BranchNotFoundError(f'Branch with id {branch_id} not found')
        return branch

    def _get_hold(self, hold_id: str) -> Hold:
        hold = self.hold_repository.get_by_id(hold_id)
        if not hold:
            raise HoldNotFoundError(f'Hold with id {hold_id} not found')
        return hold

    def find_all_holds(self) -> list[Hold]:
        return self.hold_repository.find_all()

    def get_hold(self, hold_id: str) -> Hold:
        return self._get_hold(hold_id)

    def place_hold(self, patron_id: str, item_id: str, copy_id: str | None = None) -> Hold:
        patron = self._get_patron(patron_id)
        item = self._get_item(item_id)
        copy = self._get_copy(copy_id) if copy_id else None
        hold = Hold.create(
            patron=patron,
            item=item,
            copy=copy,
            patron_holding_service=self.patron_holding_service,
            hold_policy_service=self.hold_policy_service,
        )
        created_hold = self.hold_repository.save(hold)
        event_bus.publish_events()
        return created_hold

    def ready_hold_for_pickup(self, hold_id: str, copy_id: str) -> Hold:
        copy = self._get_copy(copy_id)
        hold = self._get_hold(hold_id)
        hold.ready_for_pickup(copy=copy)
        updated_hold = self.hold_repository.save(hold)
        event_bus.publish_events()
        return updated_hold

    def pickup_hold(self, hold_id: str, staff_out_id: str, copy_id: str) -> Loan:
        copy = self._get_copy(copy_id)
        hold = self._get_hold(hold_id)
        patron = self._get_patron(hold.patron_id)
        staff = self._get_staff(staff_out_id)
        branch = self._get_branch(patron.branch_id)
        loan = Loan.create(
            copy=copy,
            patron=patron,
            staff=staff,
            branch=branch,
            patron_barring_service=self.patron_barring_service,
            loan_policy_service=self.loan_policy_service,
        )
        created_loan = self.loan_repository.save(loan, copy)
        hold.fulfill(copy=copy, loan=created_loan)
        self.hold_repository.save(hold)
        event_bus.publish_events()
        return created_loan

    def expire_hold(self, hold_id: str) -> Hold:
        hold = self._get_hold(hold_id)
        hold.expire()
        updated_hold = self.hold_repository.save(hold)
        event_bus.publish_events()
        return updated_hold

    def cancel_hold(self, hold_id: str) -> Hold:
        hold = self._get_hold(hold_id)
        hold.cancel()
        updated_hold = self.hold_repository.save(hold)
        event_bus.publish_events()
        return updated_hold

    def process_holds_for_returned_copy(self, copy_id: str) -> None:
        copy = self._get_copy(copy_id)
        holds = self.hold_repository.find_active_holds_by_item(item_id=copy.item_id)
        next_hold = holds[0] if holds else None
        if next_hold:
            self.ready_hold_for_pickup(hold_id=t.cast(str, next_hold.id), copy_id=copy_id)
            logger.info(
                'Hold ID %s is ready for pickup for patron ID %s on copy ID %s',
                next_hold.id,
                next_hold.patron_id,
                copy_id,
            )
