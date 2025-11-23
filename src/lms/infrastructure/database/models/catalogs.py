from __future__ import annotations

import enum
import uuid
import typing as t
import datetime

from sqlalchemy import UUID, Table, Column, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from ..db import BaseModel

if t.TYPE_CHECKING:
    from .serials import SerialModel, SerialIssueModel
    from .acquisitions import AcquisitionOrderLineModel
    from .circulations import HoldModel, LoanModel
    from .organizations import BranchModel


class ItemFormat(enum.Enum):
    BOOK = 'book'
    EBOOK = 'ebook'
    DVD = 'dvd'
    CD = 'cd'
    MAGAZINE = 'magazine'


class CopyStatus(enum.Enum):
    AVAILABLE = 'available'
    CHECKED_OUT = 'checked_out'
    LOST = 'lost'
    DAMAGED = 'damaged'
    RESERVED = 'reserved'


item_author_association = Table(
    'item_author_association',
    BaseModel.metadata,
    Column('item_id', UUID, ForeignKey('items.id'), primary_key=True),
    Column('author_id', UUID, ForeignKey('authors.id'), primary_key=True),
)


class PublisherModel(BaseModel):
    __tablename__ = 'publishers'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(100))

    items: Mapped[list[ItemModel]] = relationship('ItemModel', back_populates='publisher')


class AuthorModel(BaseModel):
    __tablename__ = 'authors'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str | None]
    birth_date: Mapped[datetime.date | None]

    items: Mapped[list[ItemModel]] = relationship(
        'ItemModel', secondary=item_author_association, back_populates='authors'
    )


class CategoryModel(BaseModel):
    __tablename__ = 'categories'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None]

    items: Mapped[list[ItemModel]] = relationship('ItemModel', back_populates='category')


class ItemModel(BaseModel):
    __tablename__ = 'items'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True)
    publisher_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('publishers.id'))
    publication_year: Mapped[int | None]
    category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('categories.id'))
    edition: Mapped[str | None] = mapped_column(String(50))
    format: Mapped[ItemFormat] = mapped_column(default=ItemFormat.BOOK)
    description: Mapped[str | None]

    serial: Mapped[SerialModel | None] = relationship('SerialModel', back_populates='item')
    publisher: Mapped[PublisherModel] = relationship('PublisherModel', back_populates='items')
    category: Mapped[CategoryModel] = relationship('CategoryModel', back_populates='items')
    authors: Mapped[list[AuthorModel]] = relationship(secondary=item_author_association, back_populates='items')
    copies: Mapped[list[CopyModel]] = relationship('CopyModel', back_populates='item')
    holds: Mapped[list[HoldModel]] = relationship('HoldModel', back_populates='item')
    order_lines: Mapped[list[AcquisitionOrderLineModel]] = relationship(
        'AcquisitionOrderLineModel', back_populates='item'
    )


class CopyModel(BaseModel):
    __tablename__ = 'copies'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('items.id'))
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('branches.id'))
    barcode: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[CopyStatus] = mapped_column(default=CopyStatus.AVAILABLE)
    location: Mapped[str | None] = mapped_column(String(100))
    acquisition_date: Mapped[datetime.date] = mapped_column(default=datetime.date.today)

    item: Mapped[ItemModel] = relationship('ItemModel', back_populates='copies')
    branch: Mapped[BranchModel] = relationship('BranchModel', back_populates='copies')
    loans: Mapped[list[LoanModel]] = relationship('LoanModel', back_populates='copy')
    holds: Mapped[list[HoldModel]] = relationship('HoldModel', back_populates='copy')
    serial_issues: Mapped[list[SerialIssueModel]] = relationship('SerialIssueModel', back_populates='copy')
