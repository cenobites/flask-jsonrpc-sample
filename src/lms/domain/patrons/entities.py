from __future__ import annotations

import typing as t
from decimal import Decimal
import datetime
from dataclasses import field, dataclass

from lms.domain.patrons.events import (
    FineCreatedEvent,
    PatronRegisteredEvent,
    PatronReinstatedEvent,
    PatronEmailChangedEvent,
)
from lms.domain.patrons.services import FinePolicyService
from lms.infrastructure.event_bus import event_bus
from lms.infrastructure.database.models.patrons import FineStatus, PatronStatus

from .. import DomainEntity
from .services import PatronBarringService, PatronHoldingService, PatronUniquenessService, PatronReinstatementService
from .exceptions import (
    PatronCannotBorrowError,
    DuplicatePatronEmailError,
    PatronCannotPlaceHoldError,
    PatronCannotBeReinstatedError,
    PatronCannotChangeStatusError,
)

if t.TYPE_CHECKING:
    pass


@dataclass
class Patron(DomainEntity):
    name: str
    email: str
    branch_id: str
    status: str = PatronStatus.REGISTERED.value
    member_since: datetime.date = field(default_factory=datetime.date.today)

    @classmethod
    def create(
        cls: type[Patron],
        /,
        *,
        name: str,
        email: str,
        branch_id: str,
        patron_uniqueness_service: PatronUniquenessService,
    ) -> Patron:
        if not patron_uniqueness_service.is_email_unique(email):
            raise DuplicatePatronEmailError(f'Patron with email "{email}" already exists')
        patron = cls(id=None, name=name, email=email, branch_id=branch_id)
        event_bus.add_event(PatronRegisteredEvent(patron_id=t.cast(str, patron.id), email=patron.email))
        return patron

    def is_premium_membership(self) -> bool:
        return self.member_since <= datetime.date.today() - datetime.timedelta(days=365 * 5)

    def change_email(self, email: str, patron_uniqueness_service: PatronUniquenessService) -> None:
        if email != self.email and not patron_uniqueness_service.is_email_unique(email):
            raise DuplicatePatronEmailError(f'Patron with email "{email}" already exists')
        if self.email != email:
            old_email = self.email
            self.email = email
            event_bus.add_event(
                PatronEmailChangedEvent(patron_id=t.cast(str, self.id), old_email=old_email, new_email=email)
            )

    def available_to_borrow(self, patron_barring_service: PatronBarringService) -> None:
        if self.status != PatronStatus.ACTIVE.value or not patron_barring_service.can_borrow_copies(
            t.cast(str, self.id)
        ):
            raise PatronCannotBorrowError('Patron cannot borrow this copy due to status or barring rules')

    def available_to_renew(self, copy_id: str, patron_barring_service: PatronBarringService) -> None:
        if self.status != PatronStatus.ACTIVE.value or not patron_barring_service.can_renew_copy(
            t.cast(str, self.id), copy_id
        ):
            raise PatronCannotBorrowError('Patron cannot renew this copy due to status or barring rules')

    def available_to_place_hold(self, patron_holding_service: PatronHoldingService) -> None:
        if self.status != PatronStatus.ACTIVE.value or not patron_holding_service.can_place_holds(t.cast(str, self.id)):
            raise PatronCannotPlaceHoldError('Patron cannot place hold due to status or holding rules')

    def activate(self) -> None:
        if self.status == PatronStatus.ACTIVE.value:
            raise PatronCannotChangeStatusError('Patron is already active')
        self.status = PatronStatus.ACTIVE.value

    def archive(self) -> None:
        if self.status != PatronStatus.ACTIVE.value:
            raise PatronCannotChangeStatusError('Patron is already archived')
        self.status = PatronStatus.ARCHIVED.value

    def unarchive(self) -> None:
        if self.status != PatronStatus.ARCHIVED.value:
            raise PatronCannotChangeStatusError('Patron is already active')
        self.status = PatronStatus.ACTIVE.value

    def reinstate(self, patron_reinstatement_service: PatronReinstatementService) -> None:
        if self.status != PatronStatus.SUSPENDED.value or not patron_reinstatement_service.can_reinstate(
            t.cast(str, self.id)
        ):
            raise PatronCannotBeReinstatedError('Patron is not suspended or there are loans and cannot be reinstated')
        self.status = PatronStatus.ACTIVE.value
        event_bus.add_event(PatronReinstatedEvent(patron_id=t.cast(str, self.id), email=self.email))


@dataclass
class Fine(DomainEntity):
    patron_id: str
    loan_id: str
    amount: Decimal
    reason: str | None = None
    issued_date: datetime.date = field(default_factory=datetime.date.today)
    paid_date: datetime.date | None = None
    status: str = FineStatus.CREATED.value

    @classmethod
    def create_for_overdue(
        cls: type[Fine], /, *, loan_id: str, patron_id: str, days_late: int, fine_policy_service: FinePolicyService
    ) -> Fine:
        amount = fine_policy_service.calculate_overdue_fine(days_late=days_late)
        fine = cls(
            id=None,
            patron_id=patron_id,
            loan_id=loan_id,
            amount=amount,
            reason=f'Overdue fine for loan ID {loan_id}',
            status=FineStatus.UNPAID.value,
        )
        event_bus.add_event(FineCreatedEvent(patron_id=patron_id, loan_id=loan_id, amount=amount))
        return fine

    @classmethod
    def create_for_damaged_item(
        cls: type[Fine], /, *, loan_id: str, patron_id: str, copy_id: str, fine_policy_service: FinePolicyService
    ) -> Fine:
        amount = fine_policy_service.calculate_fine_for_damaged_item(copy_id=copy_id)
        fine = cls(
            id=None,
            patron_id=patron_id,
            loan_id=loan_id,
            amount=amount,
            reason=f'Damaged fine for loan ID {loan_id}',
            status=FineStatus.UNPAID.value,
        )
        event_bus.add_event(FineCreatedEvent(patron_id=patron_id, loan_id=loan_id, amount=amount))
        return fine

    @classmethod
    def create_for_lost_item(
        cls: type[Fine], /, *, loan_id: str, patron_id: str, copy_id: str, fine_policy_service: FinePolicyService
    ) -> Fine:
        amount = fine_policy_service.calculate_fine_for_lost_item(copy_id=copy_id)
        fine = cls(
            id=None,
            patron_id=patron_id,
            loan_id=loan_id,
            amount=amount,
            reason=f'Lost fine for loan ID {loan_id}',
            status=FineStatus.UNPAID.value,
        )
        event_bus.add_event(FineCreatedEvent(patron_id=patron_id, loan_id=loan_id, amount=amount))
        return fine

    def pay(self) -> None:
        if self.status == FineStatus.PAID.value:
            raise ValueError('Fine is already paid')
        self.status = FineStatus.PAID.value
        self.paid_date = datetime.date.today()

    def waive(self) -> None:
        if self.status == FineStatus.WAIVED.value:
            raise ValueError('Fine is already waived')
        self.status = FineStatus.WAIVED.value
        self.paid_date = datetime.date.today()
