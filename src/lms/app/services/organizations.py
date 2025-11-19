from __future__ import annotations

from lms.infrastructure.event_bus import event_bus
from lms.domain.organizations.entities import Staff, Branch
from lms.domain.organizations.services import StaffUniquenessService, BranchAssignmentService, BranchUniquenessService
from lms.domain.organizations.exceptions import StaffDoesNotExistError, BranchDoesNotExistError
from lms.domain.organizations.repositories import StaffRepository, BranchRepository


class BranchService:
    def __init__(
        self,
        /,
        *,
        branch_repository: BranchRepository,
        branch_uniqueness_service: BranchUniquenessService,
        branch_assignment_service: BranchAssignmentService,
    ) -> None:
        self.branch_repository = branch_repository
        self.branch_uniqueness_service = branch_uniqueness_service
        self.branch_assignment_service = branch_assignment_service

    def _get_branch(self, branch_id: str) -> Branch:
        branch = self.branch_repository.get_by_id(branch_id)
        if branch is None:
            raise BranchDoesNotExistError()
        return branch

    def find_all_branches(self) -> list[Branch]:
        return self.branch_repository.find_all()

    def get_branch(self, branch_id: str) -> Branch:
        return self._get_branch(branch_id)

    def create_branch(
        self,
        name: str,
        address: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        manager_id: str | None = None,
    ) -> Branch:
        branch = Branch.create(
            name=name,
            email=email,
            address=address,
            phone=phone,
            branch_uniqueness_service=self.branch_uniqueness_service,
        )
        if manager_id is not None:
            branch.assign_manager(manager_id, self.branch_assignment_service)
        created_branch = self.branch_repository.save(branch)
        event_bus.publish_events()
        return created_branch

    def update_branch(
        self,
        branch_id: str,
        name: str | None = None,
        address: str | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> Branch:
        branch = self._get_branch(branch_id)
        branch.change_name(name or branch.name, self.branch_uniqueness_service)
        branch.address = address if address is not None else branch.address
        branch.phone = phone if phone is not None else branch.phone
        branch.email = email if email is not None else branch.email
        updated_branch = self.branch_repository.save(branch)
        event_bus.publish_events()
        return updated_branch

    def assign_branch_manager(self, branch_id: str, manager_id: str) -> Branch:
        branch = self._get_branch(branch_id)
        branch.assign_manager(manager_id, self.branch_assignment_service)
        updated_branch = self.branch_repository.save(branch)
        event_bus.publish_events()
        return updated_branch

    def close_branch(self, branch_id: str) -> Branch:
        branch = self._get_branch(branch_id)
        branch.close()
        updated_branch = self.branch_repository.save(branch)
        event_bus.publish_events()
        return updated_branch


class StaffService:
    def __init__(
        self, /, *, staff_repository: StaffRepository, staff_uniqueness_service: StaffUniquenessService
    ) -> None:
        self.staff_repository = staff_repository
        self.staff_uniqueness_service = staff_uniqueness_service

    def _get_staff(self, staff_id: str) -> Staff:
        staff = self.staff_repository.get_by_id(staff_id)
        if staff is None:
            raise StaffDoesNotExistError()
        return staff

    def find_all_staff(self) -> list[Staff]:
        return self.staff_repository.find_all()

    def get_staff(self, staff_id: str) -> Staff:
        return self._get_staff(staff_id)

    def create_staff(self, name: str, email: str, role: str) -> Staff:
        staff = Staff.create(name=name, email=email, role=role, staff_uniqueness_service=self.staff_uniqueness_service)
        created_staff = self.staff_repository.save(staff)
        event_bus.publish_events()
        return created_staff

    def update_staff(self, staff_id: str, name: str | None = None) -> Staff:
        staff = self._get_staff(staff_id)
        staff.name = name if name is not None else staff.name
        updated_staff = self.staff_repository.save(staff)
        event_bus.publish_events()
        return updated_staff

    def update_staff_email(self, staff_id: str, email: str) -> Staff:
        staff = self._get_staff(staff_id)
        staff.change_email(email, self.staff_uniqueness_service)
        updated_staff = self.staff_repository.save(staff)
        event_bus.publish_events()
        return updated_staff

    def assign_staff_to_branch(self, staff_id: str, branch_id: str) -> Staff:
        staff = self._get_staff(staff_id)
        staff.branch_id = branch_id
        updated_staff = self.staff_repository.save(staff)
        event_bus.publish_events()
        return updated_staff

    def assign_staff_role(self, staff_id: str, role: str) -> Staff:
        staff = self._get_staff(staff_id)
        staff.change_role(role)
        updated_staff = self.staff_repository.save(staff)
        event_bus.publish_events()
        return updated_staff

    def inactivate_staff(self, staff_id: str) -> Staff:
        staff = self._get_staff(staff_id)
        staff.mark_as_inactive()
        updated_staff = self.staff_repository.save(staff)
        event_bus.publish_events()
        return updated_staff
