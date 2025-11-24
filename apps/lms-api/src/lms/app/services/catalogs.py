from __future__ import annotations

import typing as t
import datetime

from lms.app.exceptions.catalogs import (
    CopyNotFoundError,
    ItemNotFoundError,
    AuthorNotFoundError,
    CategoryNotFoundError,
    PublisherNotFoundError,
)
from lms.domain.catalogs.entities import Copy, Item, Author, Category, Publisher
from lms.infrastructure.event_bus import event_bus
from lms.domain.catalogs.repositories import (
    CopyRepository,
    ItemRepository,
    AuthorRepository,
    CategoryRepository,
    PublisherRepository,
)


class CopyService:
    def __init__(self, /, *, copy_repository: CopyRepository) -> None:
        self.copy_repository = copy_repository

    def _get_copy(self, copy_id: str) -> Copy:
        copy = self.copy_repository.get_by_id(copy_id)
        if copy is None:
            raise CopyNotFoundError(f'Copy with id {copy_id} not found')
        return copy

    def create_copy(
        self, item_id: str, branch_id: str, barcode: str, status: str = 'available', location: str | None = None
    ) -> Copy:
        copy = Copy(id=None, item_id=item_id, branch_id=branch_id, barcode=barcode, status=status, location=location)
        return self.copy_repository.save(copy)

    def get_copy(self, copy_id: str) -> Copy:
        return self._get_copy(copy_id)

    def get_all_copies(self) -> list[Copy]:
        return self.copy_repository.find_all()

    def update_copy_status(self, copy_id: str, status: str) -> Copy:
        copy = self._get_copy(copy_id)
        updated_copy = Copy(
            id=copy.id,
            item_id=copy.item_id,
            branch_id=copy.branch_id,
            barcode=copy.barcode,
            status=status,
            location=copy.location,
            acquisition_date=copy.acquisition_date,
        )
        return self.copy_repository.save(updated_copy)

    def delete_copy(self, copy_id: str) -> bool:
        self.copy_repository.delete_by_id(copy_id)
        return True


class ItemService:
    def __init__(self, /, *, item_repository: ItemRepository, copy_repository: CopyRepository) -> None:
        self.item_repository = item_repository
        self.copy_repository = copy_repository

    def _get_item(self, item_id: str) -> Item:
        item = self.item_repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(f'Item with id {item_id} not found')
        return item

    def _get_copy(self, copy_id: str) -> Copy:
        copy = self.copy_repository.get_by_id(copy_id)
        if copy is None:
            raise CopyNotFoundError(f'Copy with id {copy_id} not found')
        return copy

    def get_all_items(self) -> list[Item]:
        return self.item_repository.find_all()

    def get_item(self, item_id: str) -> Item:
        return self._get_item(item_id)

    def create_item(
        self,
        title: str,
        format: str,
        isbn: str | None = None,
        publisher_id: str | None = None,
        publication_year: int | None = None,
        category_id: str | None = None,
        edition: str | None = None,
        description: str | None = None,
    ) -> Item:
        item = Item.create(
            title=title,
            isbn=isbn,
            publisher_id=publisher_id,
            publication_year=publication_year,
            category_id=category_id,
            edition=edition,
            format=format,
            description=description,
        )
        created_item = self.item_repository.save(item)
        event_bus.publish_events()
        return created_item

    def add_copy_to_item(
        self, item_id: str, branch_id: str, barcode: str, acquisition_date: datetime.date, location: str | None = None
    ) -> Copy:
        item = self._get_item(item_id)
        copy = Copy.create(
            item_id=t.cast(str, item.id),
            branch_id=branch_id,
            barcode=barcode,
            location=location,
            acquisition_date=acquisition_date,
        )
        created_copy = self.copy_repository.save(copy)
        event_bus.publish_events()
        return created_copy

    def update_item(
        self, item_id: str, title: str | None = None, isbn: str | None = None, description: str | None = None
    ) -> Item:
        item = self._get_item(item_id)
        item.title = title if title is not None else item.title
        item.isbn = isbn if isbn is not None else item.isbn
        item.description = description if description is not None else item.description
        updated_item = self.item_repository.save(item)
        event_bus.publish_events()
        return updated_item

    def delete_item(self, item_id: str) -> bool:
        self.item_repository.delete_by_id(item_id)
        return True


class CategoryService:
    def __init__(self, /, *, category_repository: CategoryRepository) -> None:
        self.category_repository = category_repository

    def _get_category(self, category_id: str) -> Category:
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(f'Category with id {category_id} not found')
        return category

    def find_all_categories(self) -> list[Category]:
        return self.category_repository.find_all()

    def get_category(self, category_id: str) -> Category:
        return self._get_category(category_id)

    def register_category(self, name: str, description: str | None = None) -> Category:
        category = Category.create(name=name, description=description)
        created_category = self.category_repository.save(category)
        event_bus.publish_events()
        return created_category

    def update_category(self, category_id: str, name: str | None = None, description: str | None = None) -> Category:
        category = self._get_category(category_id)
        category.name = name if name is not None else category.name
        category.description = description if description is not None else category.description
        updated_category = self.category_repository.save(category)
        event_bus.publish_events()
        return updated_category

    def delete_category(self, category_id: str) -> bool:
        self.category_repository.delete_by_id(category_id)
        return True


class AuthorService:
    def __init__(self, /, *, author_repository: AuthorRepository) -> None:
        self.author_repository = author_repository

    def _get_author(self, author_id: str) -> Author:
        author = self.author_repository.get_by_id(author_id)
        if author is None:
            raise AuthorNotFoundError(f'Author with id {author_id} not found')
        return author

    def find_all_authors(self) -> list[Author]:
        return self.author_repository.find_all()

    def get_author(self, author_id: str) -> Author:
        return self._get_author(author_id)

    def register_author(self, name: str, bio: str | None = None, birth_date: datetime.date | None = None) -> Author:
        author = Author.create(name=name, bio=bio, birth_date=birth_date)
        return self.author_repository.save(author)

    def update_author(
        self, author_id: str, name: str | None = None, bio: str | None = None, birth_date: datetime.date | None = None
    ) -> Author:
        author = self._get_author(author_id)
        author.name = name if name is not None else author.name
        author.bio = bio if bio is not None else author.bio
        author.birth_date = birth_date if birth_date is not None else author.birth_date
        updated_author = self.author_repository.save(author)
        event_bus.publish_events()
        return updated_author

    def delete_author(self, author_id: str) -> bool:
        self.author_repository.delete_by_id(author_id)
        return True


class PublisherService:
    def __init__(self, /, *, publisher_repository: PublisherRepository) -> None:
        self.publisher_repository = publisher_repository

    def _get_publisher(self, publisher_id: str) -> Publisher:
        publisher = self.publisher_repository.get_by_id(publisher_id)
        if publisher is None:
            raise PublisherNotFoundError(f'Publisher with id {publisher_id} not found')
        return publisher

    def find_all_publishers(self) -> list[Publisher]:
        return self.publisher_repository.find_all()

    def get_publisher(self, publisher_id: str) -> Publisher:
        return self._get_publisher(publisher_id)

    def register_publisher(
        self, name: str, address: str | None = None, email: str | None = None, phone: str | None = None
    ) -> Publisher:
        publisher = Publisher.create(name=name, address=address, email=email, phone=phone)
        created_publisher = self.publisher_repository.save(publisher)
        event_bus.publish_events()
        return created_publisher

    def update_publisher(
        self,
        publisher_id: str,
        name: str | None = None,
        address: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> Publisher:
        publisher = self._get_publisher(publisher_id)
        publisher.name = name if name is not None else publisher.name
        publisher.address = address if address is not None else publisher.address
        publisher.email = email if email is not None else publisher.email
        publisher.phone = phone if phone is not None else publisher.phone
        updated_publisher = self.publisher_repository.save(publisher)
        event_bus.publish_events()
        return updated_publisher

    def delete_publisher(self, publisher_id: str) -> bool:
        self.publisher_repository.delete_by_id(publisher_id)
        return True
