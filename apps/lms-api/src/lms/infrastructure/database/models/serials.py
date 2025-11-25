from __future__ import annotations

import enum
import uuid
import typing as t
import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from lms.infrastructure.database.db import BaseModel

if t.TYPE_CHECKING:
    from .catalogs import CopyModel, ItemModel


class SerialStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class SerialFrequency(enum.Enum):
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'


class SerialIssueStatus(enum.Enum):
    RECEIVED = 'received'
    MISSING = 'missing'
    LOST = 'lost'


class SerialModel(BaseModel):
    __tablename__ = 'serials'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    issn: Mapped[str] = mapped_column(String(20), unique=True)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('items.id'))
    frequency: Mapped[SerialFrequency | None]
    description: Mapped[str | None]
    status: Mapped[SerialStatus] = mapped_column(default=SerialStatus.ACTIVE)

    item: Mapped[ItemModel] = relationship('ItemModel', back_populates='serial')
    issues: Mapped[list[SerialIssueModel]] = relationship('SerialIssueModel', back_populates='serial')


class SerialIssueModel(BaseModel):
    __tablename__ = 'serial_issues'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    serial_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('serials.id'))
    issue_number: Mapped[str | None] = mapped_column(String(50))
    date_received: Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    status: Mapped[SerialIssueStatus] = mapped_column(default=SerialIssueStatus.RECEIVED)
    copy_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('copies.id'))

    serial: Mapped[SerialModel] = relationship('SerialModel', back_populates='issues')
    copy: Mapped[CopyModel | None] = relationship('CopyModel', back_populates='serial_issues')
