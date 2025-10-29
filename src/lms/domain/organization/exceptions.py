from __future__ import annotations

from .. import DomainError, DomainDoesNotExistError


class BranchBaseError(DomainError):
    pass


class BranchDoesNotExistError(DomainDoesNotExistError):
    pass


class DuplicateBranchNameError(BranchBaseError):
    pass


class CannotAssignBranchManagerError(BranchBaseError):
    pass


class BranchAlreadyClosedError(BranchBaseError):
    pass


class StaffBaseError(DomainError):
    pass


class StaffDoesNotExistError(DomainDoesNotExistError):
    pass


class DuplicateStaffEmailError(StaffBaseError):
    pass
