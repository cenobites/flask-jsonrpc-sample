from __future__ import annotations

import typing as t
import datetime
from dataclasses import field, dataclass

from lms.domain import DomainEntity
from lms.domain.catalogs.events import (
    ItemCreatedEvent,
    CopyAddedToItemEvent,
    AuthorRegisteredEvent,
    CategoryRegistedEvent,
    PublisherRegisteredEvent,
)
from lms.infrastructure.event_bus import event_bus
from lms.domain.catalogs.exceptions import CopyAlreadyLost, CopyNotAvailable, CopyNotCheckedOut, CopyAlreadyDamaged
from lms.infrastructure.database.models.catalogs import CopyStatus, ItemFormat


@dataclass
class Copy(DomainEntity):
    item_id: str
    branch_id: str
    barcode: str
    status: str = CopyStatus.AVAILABLE.value
    location: str | None = None
    acquisition_date: datetime.date = field(default_factory=datetime.date.today)

    @classmethod
    def create(
        cls,
        /,
        *,
        item_id: str,
        branch_id: str,
        barcode: str,
        location: str | None = None,
        acquisition_date: datetime.date | None = None,
    ) -> Copy:
        copy = cls(
            id=None,
            item_id=item_id,
            branch_id=branch_id,
            barcode=barcode,
            location=location,
            acquisition_date=acquisition_date or datetime.date.today(),
        )
        event_bus.add_event(CopyAddedToItemEvent(copy_id=t.cast(str, copy.id), item_id=item_id))
        return copy

    def is_older_version(self) -> bool:
        return self.acquisition_date <= datetime.date.today() - datetime.timedelta(days=365 * 2)

    def mark_as_checked_out(self) -> None:
        if self.status != CopyStatus.AVAILABLE.value:
            raise CopyNotAvailable(t.cast(str, self.id))
        self.status = CopyStatus.CHECKED_OUT.value

    def mark_as_available(self) -> None:
        if self.status != CopyStatus.CHECKED_OUT.value:
            raise CopyNotCheckedOut(t.cast(str, self.id))
        self.status = CopyStatus.AVAILABLE.value

    def mark_as_lost(self) -> None:
        if self.status == CopyStatus.LOST.value:
            raise CopyAlreadyLost(t.cast(str, self.id))
        self.status = CopyStatus.LOST.value

    def mark_as_damaged(self) -> None:
        if self.status == CopyStatus.DAMAGED.value:
            raise CopyAlreadyDamaged(t.cast(str, self.id))
        self.status = CopyStatus.DAMAGED.value


@dataclass
class Item(DomainEntity):
    title: str
    isbn: str | None = None
    publisher_id: str | None = None
    publication_year: int | None = None
    category_id: str | None = None
    edition: str | None = None
    format: str = ItemFormat.BOOK.value
    description: str | None = None

    @classmethod
    def create(
        cls,
        /,
        *,
        title: str,
        format: str = ItemFormat.BOOK.value,
        isbn: str | None = None,
        publisher_id: str | None = None,
        publication_year: int | None = None,
        category_id: str | None = None,
        edition: str | None = None,
        description: str | None = None,
    ) -> Item:
        item = cls(
            id=None,
            title=title,
            format=format,
            isbn=isbn,
            publisher_id=publisher_id,
            publication_year=publication_year,
            category_id=category_id,
            edition=edition,
            description=description,
        )
        event_bus.add_event(ItemCreatedEvent(item_id=t.cast(str, item.id)))
        return item


@dataclass
class Category(DomainEntity):
    name: str
    description: str | None = None

    @classmethod
    def create(cls, /, *, name: str, description: str | None = None) -> Category:
        category = cls(id=None, name=name, description=description)
        event_bus.add_event(CategoryRegistedEvent(category_id=t.cast(str, category.id)))
        return category


@dataclass
class Author(DomainEntity):
    name: str
    bio: str | None = None
    birth_date: datetime.date | None = None

    @classmethod
    def create(cls, /, *, name: str, bio: str | None = None, birth_date: datetime.date | None = None) -> Author:
        author = cls(id=None, name=name, bio=bio, birth_date=birth_date)
        event_bus.add_event(AuthorRegisteredEvent(author_id=t.cast(str, author.id)))
        return author


@dataclass
class Publisher(DomainEntity):
    name: str
    address: str | None = None
    email: str | None = None
    phone: str | None = None

    @classmethod
    def create(
        cls, /, *, name: str, address: str | None = None, email: str | None = None, phone: str | None = None
    ) -> Publisher:
        publisher = cls(id=None, name=name, address=address, email=email, phone=phone)
        event_bus.add_event(PublisherRegisteredEvent(publisher_id=t.cast(str, publisher.id)))
        return publisher
