from __future__ import annotations

from lms.infrastructure.database.models.organization import StaffRole

from .repositories import StaffRepository, BranchRepository


class BranchUniquenessService:
    def __init__(self, /, *, branch_repository: BranchRepository) -> None:
        self.branch_repository = branch_repository

    def is_name_unique(self, name: str) -> bool:
        return not self.branch_repository.exists_by_name(name)


class BranchAssignmentService:
    def __init__(self, /, *, branch_repository: BranchRepository, staff_repository: StaffRepository) -> None:
        self.branch_repository = branch_repository
        self.staff_repository = staff_repository

    def can_assign_manager(self, branch_id: str, manager_id: str) -> bool:
        branch = self.branch_repository.get_by_id(branch_id)
        if branch is None:
            return False
        manager = self.staff_repository.get_by_id(manager_id)
        return manager is not None and manager.role == StaffRole.MANAGER.value


class StaffUniquenessService:
    def __init__(self, /, *, staff_repository: StaffRepository) -> None:
        self.staff_repository = staff_repository

    def is_email_unique(self, email: str) -> bool:
        return not self.staff_repository.exists_by_email(email)
