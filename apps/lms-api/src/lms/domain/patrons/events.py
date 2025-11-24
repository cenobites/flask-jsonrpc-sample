from __future__ import annotations

from decimal import Decimal
from dataclasses import dataclass

from lms.domain import DomainEvent


@dataclass
class PatronRegisteredEvent(DomainEvent):
    patron_id: str
    email: str


@dataclass
class PatronEmailChangedEvent(DomainEvent):
    patron_id: str
    old_email: str
    new_email: str


@dataclass
class PatronSuspendedEvent(DomainEvent):
    patron_id: str
    email: str


@dataclass
class PatronReinstatedEvent(DomainEvent):
    patron_id: str
    email: str


@dataclass
class FineCreatedEvent(DomainEvent):
    patron_id: str
    loan_id: str
    amount: Decimal


@dataclass
class FinePaidEvent(DomainEvent):
    patron_id: str
    loan_id: str
    amount: Decimal
