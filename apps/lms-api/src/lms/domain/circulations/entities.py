from __future__ import annotations

import typing as t
import datetime
from dataclasses import field, dataclass

from lms.domain import DomainEntity
from lms.domain.patrons.services import PatronBarringService, PatronHoldingService
from lms.infrastructure.event_bus import event_bus
from lms.infrastructure.database.models.circulations import HoldStatus

from .events import (
    HoldReadyEvent,
    HoldExpiredEvent,
    LoanCreatedEvent,
    LoanDamagedEvent,
    LoanOverdueEvent,
    LoanReturnedEvent,
    HoldCancelledEvent,
    HoldFulfilledEvent,
    LoanMarkedLostEvent,
)
from .services import HoldPolicyService, LoanPolicyService
from .exceptions import LoanOverdue, HoldNotPending, LoanAlreadyReturned

if t.TYPE_CHECKING:
    from lms.domain.patrons.entities import Patron
    from lms.domain.catalogs.entities import Copy, Item
    from lms.domain.organizations.entities import Staff, Branch


@dataclass
class Loan(DomainEntity):
    copy_id: str
    patron_id: str
    branch_id: str
    staff_out_id: str
    due_date: datetime.date
    loan_date: datetime.date = field(default_factory=datetime.date.today)
    return_date: datetime.date | None = None
    staff_in_id: str | None = None

    @classmethod
    def create(
        cls: type[Loan],
        /,
        *,
        copy: Copy,
        patron: Patron,
        staff: Staff,
        branch: Branch,
        patron_barring_service: PatronBarringService,
        loan_policy_service: LoanPolicyService,
    ) -> Loan:
        patron.available_to_borrow(patron_barring_service)
        copy.mark_as_checked_out()
        loan_date = datetime.date.today()
        due_date = loan_policy_service.calculate_due_date(loan_date=loan_date, patron=patron, copy=copy)
        loan = cls(
            id=None,
            copy_id=t.cast(str, copy.id),
            patron_id=t.cast(str, patron.id),
            branch_id=t.cast(str, branch.id),
            staff_out_id=t.cast(str, staff.id),
            loan_date=loan_date,
            due_date=due_date,
        )
        event_bus.add_event(
            LoanCreatedEvent(
                loan_id=t.cast(str, loan.id),
                copy_id=loan.copy_id,
                patron_id=loan.patron_id,
                branch_id=loan.branch_id,
                staff_out_id=loan.staff_out_id,
                loan_date=loan.loan_date,
                due_date=loan.due_date,
            )
        )
        return loan

    def mark_as_returned(self, copy: Copy, return_date: datetime.date, staff_in_id: str) -> None:
        copy.mark_as_available()
        if self.return_date is not None:
            raise LoanAlreadyReturned(t.cast(str, self.id), self.return_date)
        self.return_date = return_date
        self.staff_in_id = staff_in_id
        event_bus.add_event(
            LoanReturnedEvent(
                loan_id=t.cast(str, self.id),
                copy_id=self.copy_id,
                patron_id=self.patron_id,
                branch_id=self.branch_id,
                staff_in_id=self.staff_in_id,
                loan_date=self.loan_date,
                due_date=self.due_date,
                return_date=self.return_date,
            )
        )
        if self.return_date > self.due_date:
            days_late = (return_date - self.due_date).days
            event_bus.add_event(
                LoanOverdueEvent(loan_id=t.cast(str, self.id), days_late=days_late, patron_id=self.patron_id)
            )

    def mark_damaged(self, copy: Copy) -> None:
        copy.mark_as_damaged()
        if self.return_date is not None:
            raise LoanAlreadyReturned(t.cast(str, self.id), self.return_date)
        if self.due_date < datetime.date.today():
            days_late = (datetime.date.today() - self.due_date).days
            raise LoanOverdue(t.cast(str, self.id), days_late)
        self.return_date = datetime.date.today()
        event_bus.add_event(
            LoanDamagedEvent(
                loan_id=t.cast(str, self.id), copy_id=self.copy_id, patron_id=self.patron_id, branch_id=self.branch_id
            )
        )

    def mark_lost(self, copy: Copy) -> None:
        copy.mark_as_lost()
        if self.return_date is not None:
            raise LoanAlreadyReturned(t.cast(str, self.id), self.return_date)
        if self.due_date < datetime.date.today():
            days_late = (datetime.date.today() - self.due_date).days
            raise LoanOverdue(t.cast(str, self.id), days_late)
        self.return_date = datetime.date.today()
        event_bus.add_event(
            LoanMarkedLostEvent(
                loan_id=t.cast(str, self.id), copy_id=self.copy_id, patron_id=self.patron_id, branch_id=self.branch_id
            )
        )

    def renew(
        self,
        patron: Patron,
        copy: Copy,
        patron_barring_service: PatronBarringService,
        loan_policy_service: LoanPolicyService,
    ) -> None:
        patron.available_to_renew(copy_id=t.cast(str, copy.id), patron_barring_service=patron_barring_service)
        if self.return_date is not None:
            raise LoanAlreadyReturned(t.cast(str, self.id), self.return_date)
        if self.due_date < datetime.date.today():
            days_late = (datetime.date.today() - self.due_date).days
            raise LoanOverdue(t.cast(str, self.id), days_late)
        self.due_date = loan_policy_service.calculate_new_due_date(patron=patron, copy=copy)


@dataclass
class Hold(DomainEntity):
    item_id: str
    patron_id: str
    copy_id: str | None = None
    loan_id: str | None = None
    request_date: datetime.date = field(default_factory=datetime.date.today)
    expiry_date: datetime.date | None = None
    status: str = HoldStatus.PENDING.value

    @classmethod
    def create(
        cls: type[Hold],
        /,
        *,
        patron: Patron,
        item: Item,
        copy: Copy | None = None,
        patron_holding_service: PatronHoldingService,
        hold_policy_service: HoldPolicyService,
    ) -> Hold:
        patron.available_to_place_hold(patron_holding_service)
        # item.can_be_held()
        request_date = datetime.date.today()
        expiry_date = hold_policy_service.calculate_hold_expiry_date(request_date=request_date)
        hold = cls(
            id=None,
            patron_id=t.cast(str, patron.id),
            item_id=t.cast(str, item.id),
            copy_id=copy.id if copy else None,
            expiry_date=expiry_date,
            status=HoldStatus.PENDING.value,
        )
        return hold

    def ready_for_pickup(self, copy: Copy) -> None:
        if self.status != HoldStatus.PENDING.value:
            raise HoldNotPending(t.cast(str, self.id))
        self.copy_id = t.cast(str, copy.id)
        self.status = HoldStatus.READY.value
        event_bus.add_event(
            HoldReadyEvent(
                hold_id=t.cast(str, self.id), copy_id=self.copy_id, patron_id=self.patron_id, item_id=self.item_id
            )
        )

    def fulfill(self, copy: Copy, loan: Loan) -> None:
        if self.status != HoldStatus.PENDING.value:
            raise HoldNotPending(t.cast(str, self.id))
        self.copy_id = t.cast(str, copy.id)
        self.loan_id = t.cast(str, loan.id)
        self.status = HoldStatus.FULFILLED.value
        event_bus.add_event(
            HoldFulfilledEvent(
                hold_id=t.cast(str, self.id),
                copy_id=self.copy_id,
                loan_id=t.cast(str, loan.id),
                patron_id=self.patron_id,
                item_id=self.item_id,
                request_date=self.request_date,
                expiry_date=t.cast(datetime.date, self.expiry_date),
            )
        )

    def expire(self) -> None:
        if self.status != HoldStatus.PENDING.value:
            raise HoldNotPending(t.cast(str, self.id))
        self.status = HoldStatus.EXPIRED.value
        event_bus.add_event(
            HoldExpiredEvent(
                hold_id=t.cast(str, self.id), patron_id=self.patron_id, item_id=self.item_id, copy_id=self.copy_id
            )
        )

    def cancel(self) -> None:
        if self.status != HoldStatus.PENDING.value:
            raise HoldNotPending(t.cast(str, self.id))
        self.status = HoldStatus.CANCELLED.value
        event_bus.add_event(
            HoldCancelledEvent(
                hold_id=t.cast(str, self.id), patron_id=self.patron_id, item_id=self.item_id, copy_id=self.copy_id
            )
        )
