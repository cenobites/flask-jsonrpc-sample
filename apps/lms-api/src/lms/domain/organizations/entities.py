from __future__ import annotations

import typing as t
import datetime
from dataclasses import field, dataclass

from lms.domain import DomainEntity
from lms.infrastructure.event_bus import event_bus
from lms.infrastructure.database.models.organizations import StaffRole, StaffStatus, BranchStatus

from .events import (
    BranchClosedEvent,
    BranchOpenedEvent,
    BranchNameChangedEvent,
    StaffEmailChangedEvent,
    ManagerAssignedToBranchEvent,
)
from .services import StaffUniquenessService, BranchAssignmentService, BranchUniquenessService
from .exceptions import (
    StaffNotActive,
    StaffNotManager,
    BranchAlreadyClosed,
    BranchNameAlreadyExists,
    StaffEmailAlreadyExists,
)


@dataclass
class Branch(DomainEntity):
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str = BranchStatus.OPEN.value
    manager_id: str | None = None

    @classmethod
    def create(
        cls,
        /,
        *,
        name: str,
        address: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        branch_uniqueness_service: BranchUniquenessService,
    ) -> Branch:
        if not branch_uniqueness_service.is_name_unique(name):
            raise BranchNameAlreadyExists(name)
        branch = cls(id=None, name=name, address=address, phone=phone, email=email)
        event_bus.add_event(BranchOpenedEvent(branch_id=t.cast(str, branch.id), branch_name=branch.name))
        return branch

    def change_name(self, name: str, branch_uniqueness_service: BranchUniquenessService) -> None:
        if name != self.name and not branch_uniqueness_service.is_name_unique(name):
            raise BranchNameAlreadyExists(name)
        if self.name != name:
            self.name = name
            event_bus.add_event(
                BranchNameChangedEvent(branch_id=t.cast(str, self.id), old_name=self.name, new_name=name)
            )

    def assign_manager(self, manager_id: str, branch_assignment_service: BranchAssignmentService) -> None:
        if not branch_assignment_service.can_assign_manager(t.cast(str, self.id), manager_id):
            raise StaffNotManager(manager_id)
        if self.manager_id != manager_id:
            self.manager_id = manager_id
            self.status = BranchStatus.ACTIVE.value
            event_bus.add_event(ManagerAssignedToBranchEvent(branch_id=t.cast(str, self.id), manager_id=manager_id))

    def close(self) -> None:
        if self.status == BranchStatus.CLOSED.value:
            raise BranchAlreadyClosed(t.cast(str, self.id))
        self.status = BranchStatus.CLOSED.value
        event_bus.add_event(BranchClosedEvent(branch_id=t.cast(str, self.id)))


@dataclass
class Staff(DomainEntity):
    name: str
    email: str
    branch_id: str | None = None
    role: str = StaffRole.LIBRARIAN.value
    hire_date: datetime.date = field(default_factory=datetime.date.today)
    status: str = StaffStatus.ACTIVE.value

    @classmethod
    def create(cls, /, *, name: str, email: str, role: str, staff_uniqueness_service: StaffUniquenessService) -> Staff:
        if not staff_uniqueness_service.is_email_unique(email):
            raise StaffEmailAlreadyExists(email)
        staff = cls(id=None, name=name, email=email, role=role)
        return staff

    def change_email(self, email: str, staff_uniqueness_service: StaffUniquenessService) -> None:
        if email != self.email and not staff_uniqueness_service.is_email_unique(email):
            raise StaffEmailAlreadyExists(email)
        if self.email != email:
            old_email = self.email
            self.email = email
            event_bus.add_event(
                StaffEmailChangedEvent(staff_id=t.cast(str, self.id), old_email=old_email, new_email=email)
            )

    def change_role(self, role: str) -> None:
        self.role = StaffRole(role).value

    def mark_as_inactive(self) -> None:
        if self.status != StaffStatus.ACTIVE.value:
            raise StaffNotActive(t.cast(str, self.id))
        self.status = StaffStatus.INACTIVE.value
