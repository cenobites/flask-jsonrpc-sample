from __future__ import annotations

import pytest
from pydantic import ValidationError

from lms.app.schemas.catalogs import ItemCreate, ItemUpdate
from lms.infrastructure.database.models.catalogs import ItemFormat


def test_item_create_minimal_fields() -> None:
    item = ItemCreate(title='The Great Gatsby')

    assert item.title == 'The Great Gatsby'
    assert item.isbn is None
    assert item.publisher_id is None
    assert item.publication_year is None
    assert item.category_id is None
    assert item.edition is None
    assert item.format == ItemFormat.BOOK
    assert item.description is None


def test_item_create_all_fields() -> None:
    item = ItemCreate(
        title='1984',
        isbn='978-0451524935',
        publisher_id='pub-123',
        publication_year=1949,
        category_id='cat-456',
        edition='First Edition',
        format=ItemFormat.EBOOK,
        description='A dystopian social science fiction novel',
    )

    assert item.title == '1984'
    assert item.isbn == '978-0451524935'
    assert item.publisher_id == 'pub-123'
    assert item.publication_year == 1949
    assert item.category_id == 'cat-456'
    assert item.edition == 'First Edition'
    assert item.format == 'ebook'
    assert item.description == 'A dystopian social science fiction novel'


def test_item_create_requires_title() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ItemCreate()  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('title',) for error in errors)


def test_item_create_default_format() -> None:
    item = ItemCreate(title='Test Book')

    assert item.format == ItemFormat.BOOK


def test_item_create_with_different_formats() -> None:
    formats = [
        (ItemFormat.BOOK, 'book'),
        (ItemFormat.EBOOK, 'ebook'),
        (ItemFormat.DVD, 'dvd'),
        (ItemFormat.CD, 'cd'),
        (ItemFormat.MAGAZINE, 'magazine'),
    ]

    for fmt_enum, fmt_str in formats:
        item = ItemCreate(title='Test Item', format=fmt_enum)
        assert item.format == fmt_str


def test_item_create_with_publication_year() -> None:
    test_years = [1900, 1950, 2000, 2025]

    for year in test_years:
        item = ItemCreate(title='Test Book', publication_year=year)
        assert item.publication_year == year


def test_item_create_strips_whitespace() -> None:
    item = ItemCreate(title='  Test Title  ', isbn='  123-456  ', edition='  First  ')

    assert item.title == 'Test Title'
    assert item.isbn == '123-456'
    assert item.edition == 'First'


def test_item_update_requires_id_and_title() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ItemUpdate(id='item-123')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('title',) for error in errors)


def test_item_update_all_fields() -> None:
    item = ItemUpdate(
        id='item-123',
        title='Updated Title',
        isbn='978-1234567890',
        publisher_id='pub-789',
        publication_year=2024,
        category_id='cat-999',
        edition='Second Edition',
        format=ItemFormat.CD,
        description='Updated description',
    )

    assert item.id == 'item-123'
    assert item.title == 'Updated Title'
    assert item.isbn == '978-1234567890'
    assert item.publisher_id == 'pub-789'
    assert item.publication_year == 2024
    assert item.category_id == 'cat-999'
    assert item.edition == 'Second Edition'
    assert item.format == 'cd'
    assert item.description == 'Updated description'


def test_item_update_minimal_fields() -> None:
    item = ItemUpdate(id='item-123', title='Test Title')

    assert item.id == 'item-123'
    assert item.title == 'Test Title'
    assert item.isbn is None
    assert item.format == ItemFormat.BOOK


def test_item_update_with_none_values() -> None:
    item = ItemUpdate(
        id='item-123',
        title='Test',
        isbn=None,
        publisher_id=None,
        publication_year=None,
        category_id=None,
        edition=None,
        description=None,
    )

    assert item.isbn is None
    assert item.publisher_id is None
    assert item.publication_year is None
    assert item.category_id is None
    assert item.edition is None
    assert item.description is None


def test_item_create_serialization() -> None:
    item = ItemCreate(title='Test Book', isbn='123-456', format=ItemFormat.EBOOK)
    data = item.model_dump()

    assert data['title'] == 'Test Book'
    assert data['isbn'] == '123-456'
    assert data['format'] == 'ebook'  # Enum value


def test_item_update_serialization() -> None:
    item = ItemUpdate(id='item-1', title='Test', format=ItemFormat.DVD)
    data = item.model_dump()

    assert data['id'] == 'item-1'
    assert data['title'] == 'Test'
    assert data['format'] == 'dvd'  # Enum value


def test_item_create_long_title() -> None:
    long_title = 'A' * 500
    item = ItemCreate(title=long_title)

    assert item.title == long_title


def test_item_create_long_description() -> None:
    # Use a moderate length description that won't break the system
    # Note: str_strip_whitespace config strips trailing spaces
    description = ('Lorem ipsum ' * 50).strip()  # About 600 characters
    item = ItemCreate(title='Test', description=description)

    assert item.description == description


def test_item_update_format_change() -> None:
    item = ItemUpdate(id='item-1', title='Test', format=ItemFormat.BOOK)
    assert item.format == 'book'

    item2 = ItemUpdate(id='item-1', title='Test', format=ItemFormat.EBOOK)
    assert item2.format == 'ebook'
