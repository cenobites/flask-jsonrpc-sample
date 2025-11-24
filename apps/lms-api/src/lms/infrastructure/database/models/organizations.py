from __future__ import annotations

import enum
import uuid
import typing as t
import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from lms.infrastructure.database.db import BaseModel

if t.TYPE_CHECKING:
    from .patrons import PatronModel
    from .catalogs import CopyModel
    from .acquisitions import AcquisitionOrderModel
    from .circulations import LoanModel


class BranchStatus(enum.Enum):
    OPEN = 'open'
    ACTIVE = 'active'
    CLOSED = 'closed'


class StaffRole(enum.Enum):
    LIBRARIAN = 'librarian'
    TECHNICIAN = 'technician'
    MANAGER = 'manager'


class StaffStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class BranchModel(BaseModel):
    __tablename__ = 'branches'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    manager_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('staff.id', use_alter=True), name='manager_id_fk')
    status: Mapped[BranchStatus] = mapped_column(default=BranchStatus.OPEN)

    manager: Mapped[StaffModel] = relationship('StaffModel', back_populates='managed_branch', foreign_keys=[manager_id])
    staff: Mapped[list[StaffModel]] = relationship(
        'StaffModel', back_populates='branch', foreign_keys='StaffModel.branch_id'
    )
    patrons: Mapped[list[PatronModel]] = relationship('PatronModel', back_populates='branch')
    copies: Mapped[list[CopyModel]] = relationship('CopyModel', back_populates='branch')
    loans: Mapped[list[LoanModel]] = relationship('LoanModel', back_populates='branch')


class StaffModel(BaseModel):
    __tablename__ = 'staff'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped[StaffRole] = mapped_column(default=StaffRole.LIBRARIAN)
    branch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('branches.id'))
    hire_date: Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    status: Mapped[StaffStatus] = mapped_column(default=StaffStatus.ACTIVE)

    branch: Mapped[BranchModel | None] = relationship('BranchModel', back_populates='staff', foreign_keys=[branch_id])
    managed_branch: Mapped[BranchModel | None] = relationship(
        'BranchModel', back_populates='manager', foreign_keys='BranchModel.manager_id'
    )
    checked_out_loans: Mapped[list[LoanModel]] = relationship(
        'LoanModel', back_populates='staff_out', foreign_keys='LoanModel.staff_out_id'
    )
    checked_in_loans: Mapped[list[LoanModel]] = relationship(
        'LoanModel', back_populates='staff_in', foreign_keys='LoanModel.staff_in_id'
    )
    acquisition_orders: Mapped[list[AcquisitionOrderModel]] = relationship(
        'AcquisitionOrderModel', back_populates='staff'
    )
