from __future__ import annotations

from lms.domain import DomainError


class BranchNameAlreadyExists(DomainError):
    def __init__(self, name: str, /) -> None:
        super().__init__(f'Branch with name {name!r} already exists')
        self.name = name


class StaffNotManager(DomainError):
    def __init__(self, staff_id: str, /) -> None:
        super().__init__(f'Staff with id {staff_id} is not a manager')
        self.staff_id = staff_id


class BranchAlreadyClosed(DomainError):
    def __init__(self, branch_id: str, /) -> None:
        super().__init__(f'Branch {branch_id} is already closed')
        self.branch_id = branch_id


class StaffEmailAlreadyExists(DomainError):
    def __init__(self, email: str, /) -> None:
        super().__init__(f'Staff with email {email!r} already exists')
        self.email = email


class StaffNotActive(DomainError):
    def __init__(self, staff_id: str, /) -> None:
        super().__init__(f'Staff {staff_id} is not active')
        self.staff_id = staff_id
