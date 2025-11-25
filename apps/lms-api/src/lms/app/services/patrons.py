from __future__ import annotations

from lms.domain import DomainError
from lms.app.exceptions import ServiceFailed
from lms.app.exceptions.patrons import FineNotFoundError, PatronNotFoundError
from lms.domain.patrons.entities import Fine, Patron
from lms.domain.patrons.services import FinePolicyService, PatronUniquenessService, PatronReinstatementService
from lms.infrastructure.event_bus import event_bus
from lms.domain.patrons.exceptions import PatronAlreadyActive
from lms.domain.patrons.repositories import FineRepository, PatronRepository


class PatronService:
    def __init__(
        self,
        /,
        *,
        patron_repository: PatronRepository,
        patron_uniqueness_service: PatronUniquenessService,
        patron_reinstatement_service: PatronReinstatementService,
    ) -> None:
        self.patron_repository = patron_repository
        self.patron_uniqueness_service = patron_uniqueness_service
        self.patron_reinstatement_service = patron_reinstatement_service

    def _get_patron(self, patron_id: str) -> Patron:
        patron = self.patron_repository.get_by_id(patron_id)
        if patron is None:
            raise PatronNotFoundError(f'Patron with id {patron_id} not found')
        return patron

    def find_all_patrons(self) -> list[Patron]:
        return self.patron_repository.find_all()

    def get_patron(self, patron_id: str) -> Patron:
        return self._get_patron(patron_id)

    def create_patron(self, branch_id: str, name: str, email: str) -> Patron:
        try:
            patron = Patron.create(
                branch_id=branch_id, name=name, email=email, patron_uniqueness_service=self.patron_uniqueness_service
            )
            patron.activate()
        except PatronAlreadyActive as e:
            raise ServiceFailed('The patron cannot be created as active', cause=e) from e
        except DomainError as e:
            raise ServiceFailed('The patron cannot be created', cause=e) from e
        created_patron = self.patron_repository.save(patron)
        event_bus.publish_events()
        return created_patron

    def update_patron(self, patron_id: str, name: str | None) -> Patron:
        patron = self._get_patron(patron_id)
        patron.name = name if name is not None else patron.name
        updated_patron = self.patron_repository.save(patron)
        event_bus.publish_events()
        return updated_patron

    def update_patron_email(self, patron_id: str, email: str) -> Patron:
        patron = self._get_patron(patron_id)
        try:
            patron.change_email(email, self.patron_uniqueness_service)
        except DomainError as e:
            raise ServiceFailed('The patron email cannot be updated', cause=e) from e
        updated_patron = self.patron_repository.save(patron)
        event_bus.publish_events()
        return updated_patron

    def activate_patron(self, patron_id: str) -> Patron:
        patron = self._get_patron(patron_id)
        try:
            patron.activate()
        except DomainError as e:
            raise ServiceFailed('The patron cannot be activated', cause=e) from e
        updated_patron = self.patron_repository.save(patron)
        event_bus.publish_events()
        return updated_patron

    def reinstate_patron(self, patron_id: str) -> Patron:
        patron = self._get_patron(patron_id)
        try:
            patron.reinstate(self.patron_reinstatement_service)
        except DomainError as e:
            raise ServiceFailed('The patron cannot be reinstated', cause=e) from e
        updated_patron = self.patron_repository.save(patron)
        event_bus.publish_events()
        return updated_patron

    def archive_patron(self, patron_id: str) -> Patron:
        patron = self._get_patron(patron_id)
        try:
            patron.archive()
        except DomainError as e:
            raise ServiceFailed('The patron cannot be archived', cause=e) from e
        updated_patron = self.patron_repository.save(patron)
        event_bus.publish_events()
        return updated_patron

    def unarchive_patron(self, patron_id: str) -> Patron:
        patron = self._get_patron(patron_id)
        try:
            patron.unarchive()
        except DomainError as e:
            raise ServiceFailed('The patron cannot be unarchived', cause=e) from e
        updated_patron = self.patron_repository.save(patron)
        event_bus.publish_events()
        return updated_patron


class FineService:
    def __init__(self, /, *, fine_repository: FineRepository, fine_policy_service: FinePolicyService) -> None:
        self.fine_repository = fine_repository
        self.fine_policy_service = fine_policy_service

    def _get_fine(self, fine_id: str) -> Fine:
        fine = self.fine_repository.get_by_id(fine_id)
        if fine is None:
            raise FineNotFoundError(f'Fine with id {fine_id} not found')
        return fine

    def find_all_fines(self) -> list[Fine]:
        return self.fine_repository.find_all()

    def get_fine(self, fine_id: str) -> Fine:
        return self._get_fine(fine_id)

    def pay_fine(self, fine_id: str) -> Fine:
        fine = self._get_fine(fine_id)
        try:
            fine.pay()
        except DomainError as e:
            raise ServiceFailed('The fine cannot be paid', cause=e) from e
        updated_fine = self.fine_repository.save(fine)
        event_bus.publish_events()
        return updated_fine

    def waive_fine(self, fine_id: str) -> Fine:
        fine = self._get_fine(fine_id)
        try:
            fine.waive()
        except DomainError as e:
            raise ServiceFailed('The fine cannot be waived', cause=e) from e
        updated_fine = self.fine_repository.save(fine)
        event_bus.publish_events()
        return updated_fine

    def process_overdue_loan(self, loan_id: str, patron_id: str, days_late: int) -> Fine:
        try:
            fine = Fine.create_for_overdue(
                loan_id=loan_id, patron_id=patron_id, days_late=days_late, fine_policy_service=self.fine_policy_service
            )
        except DomainError as e:
            raise ServiceFailed('The overdue loan cannot be processed for fine', cause=e) from e
        created_fine = self.fine_repository.save(fine)
        event_bus.publish_events()
        return created_fine
