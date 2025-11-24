from __future__ import annotations

import enum
import uuid
import typing as t
from decimal import Decimal
import datetime

from sqlalchemy import DECIMAL, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from lms.infrastructure.database.db import BaseModel

if t.TYPE_CHECKING:
    from .circulations import HoldModel, LoanModel
    from .organizations import BranchModel


class PatronStatus(enum.Enum):
    REGISTERED = 'registered'
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    ARCHIVED = 'archived'


class FineStatus(enum.Enum):
    CREATED = 'created'
    PAID = 'paid'
    UNPAID = 'unpaid'
    WAIVED = 'waived'


class PatronModel(BaseModel):
    __tablename__ = 'patrons'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('branches.id'))
    member_since: Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    status: Mapped[PatronStatus] = mapped_column(default=PatronStatus.REGISTERED)

    branch: Mapped[BranchModel] = relationship('BranchModel', back_populates='patrons')
    loans: Mapped[list[LoanModel]] = relationship('LoanModel', back_populates='patron')
    holds: Mapped[list[HoldModel]] = relationship('HoldModel', back_populates='patron')
    fines: Mapped[list[FineModel]] = relationship('FineModel', back_populates='patron')


class FineModel(BaseModel):
    __tablename__ = 'fines'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    patron_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('patrons.id'))
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    reason: Mapped[str | None]
    issued_date: Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    paid_date: Mapped[datetime.date | None]
    status: Mapped[FineStatus] = mapped_column(default=FineStatus.CREATED)

    patron: Mapped[PatronModel] = relationship('PatronModel', back_populates='fines')
