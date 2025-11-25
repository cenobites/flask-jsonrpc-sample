from __future__ import annotations

from dataclasses import dataclass

from lms.domain import DomainEvent


@dataclass
class CopyAddedToItemEvent(DomainEvent):
    copy_id: str
    item_id: str


@dataclass
class CopyWithdrawnEvent(DomainEvent):
    copy_id: str


@dataclass
class ItemCreatedEvent(DomainEvent):
    item_id: str


@dataclass
class CategoryRegistedEvent(DomainEvent):
    category_id: str


@dataclass
class AuthorRegisteredEvent(DomainEvent):
    author_id: str


@dataclass
class PublisherRegisteredEvent(DomainEvent):
    publisher_id: str
