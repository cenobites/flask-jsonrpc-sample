from __future__ import annotations

from datetime import date
from dataclasses import dataclass

from .. import DomainEvent


@dataclass
class LoanCreatedEvent(DomainEvent):
    loan_id: str
    copy_id: str
    patron_id: str
    branch_id: str
    staff_out_id: str
    loan_date: date
    due_date: date | None


@dataclass
class LoanReturnedEvent(DomainEvent):
    loan_id: str
    copy_id: str
    patron_id: str
    branch_id: str
    staff_in_id: str
    loan_date: date
    due_date: date
    return_date: date


@dataclass
class LoanMarkedLostEvent(DomainEvent):
    loan_id: str
    copy_id: str
    patron_id: str
    branch_id: str


@dataclass
class LoanDamagedEvent(DomainEvent):
    loan_id: str
    copy_id: str
    patron_id: str
    branch_id: str


@dataclass
class LoanOverdueEvent(DomainEvent):
    loan_id: str
    patron_id: str
    days_late: int


@dataclass
class HoldPlacedEvent(DomainEvent):
    hold_id: str
    patron_id: str
    item_id: str


@dataclass
class HoldReadyEvent(DomainEvent):
    hold_id: str
    patron_id: str
    item_id: str
    copy_id: str


@dataclass
class HoldFulfilledEvent(DomainEvent):
    hold_id: str
    patron_id: str
    item_id: str
    copy_id: str
    loan_id: str
    request_date: date
    expiry_date: date


@dataclass
class HoldExpiredEvent(DomainEvent):
    hold_id: str
    patron_id: str
    item_id: str
    copy_id: str | None


@dataclass
class HoldCancelledEvent(DomainEvent):
    hold_id: str
    patron_id: str
    item_id: str
    copy_id: str | None
