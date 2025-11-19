from __future__ import annotations

from dataclasses import dataclass

from .. import DomainEvent


@dataclass
class BranchOpenedEvent(DomainEvent):
    branch_id: str
    branch_name: str


@dataclass
class BranchNameChangedEvent(DomainEvent):
    branch_id: str
    old_name: str
    new_name: str


@dataclass
class ManagerAssignedToBranchEvent(DomainEvent):
    branch_id: str
    manager_id: str


@dataclass
class BranchClosedEvent(DomainEvent):
    branch_id: str


@dataclass
class StaffAssignedToBranchEvent(DomainEvent):
    branch_id: str
    staff_id: str
    role: str


@dataclass
class StaffEmailChangedEvent(DomainEvent):
    staff_id: str
    old_email: str
    new_email: str
