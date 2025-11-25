from __future__ import annotations

import enum
import uuid
import typing as t
import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from lms.infrastructure.database.db import BaseModel

if t.TYPE_CHECKING:
    from .patrons import PatronModel
    from .catalogs import CopyModel, ItemModel
    from .organizations import StaffModel, BranchModel


class HoldStatus(enum.Enum):
    PENDING = 'pending'
    READY = 'ready'
    FULFILLED = 'fulfilled'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'


class LoanModel(BaseModel):
    __tablename__ = 'loans'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    copy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('copies.id'))
    patron_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('patrons.id'))
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('branches.id'))
    staff_out_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('staff.id'))
    staff_in_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('staff.id'))
    loan_date: Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    due_date: Mapped[datetime.date]
    return_date: Mapped[datetime.date | None]

    branch: Mapped[BranchModel] = relationship('BranchModel', back_populates='loans')
    copy: Mapped[CopyModel] = relationship('CopyModel', back_populates='loans')
    patron: Mapped[PatronModel] = relationship('PatronModel', back_populates='loans')
    staff_out: Mapped[StaffModel] = relationship(
        'StaffModel', back_populates='checked_out_loans', foreign_keys=[staff_out_id]
    )
    staff_in: Mapped[StaffModel] = relationship(
        'StaffModel', back_populates='checked_in_loans', foreign_keys=[staff_in_id]
    )
    hold: Mapped[HoldModel] = relationship('HoldModel', back_populates='loan')


class HoldModel(BaseModel):
    __tablename__ = 'holds'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    patron_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('patrons.id'))
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('items.id'))
    loan_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('loans.id'))
    copy_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('copies.id'))
    request_date: Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    expiry_date: Mapped[datetime.date | None]
    status: Mapped[HoldStatus] = mapped_column(default=HoldStatus.PENDING)

    patron: Mapped[PatronModel] = relationship('PatronModel', back_populates='holds')
    item: Mapped[ItemModel] = relationship('ItemModel', back_populates='holds')
    loan: Mapped[LoanModel] = relationship('LoanModel', back_populates='hold')
    copy: Mapped[CopyModel] = relationship('CopyModel', back_populates='holds')
