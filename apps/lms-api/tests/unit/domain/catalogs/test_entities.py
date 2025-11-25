from __future__ import annotations

import datetime
from unittest.mock import patch
from collections.abc import Iterator

import pytest

from lms.domain.catalogs.entities import Copy, Item, Author, Category, Publisher
from lms.domain.catalogs.exceptions import CopyAlreadyLost, CopyNotAvailable, CopyNotCheckedOut, CopyAlreadyDamaged
from lms.infrastructure.database.models.catalogs import CopyStatus, ItemFormat


@pytest.fixture
def mock_event_bus() -> Iterator:
    with patch('lms.domain.catalogs.entities.event_bus') as mock_bus:
        yield mock_bus


class TestCopy:
    def test_create_copy(self, mock_event_bus: object) -> None:
        copy = Copy.create(item_id='item1', branch_id='branch1', barcode='BAR123456', location='A1-B2')

        assert copy.item_id == 'item1'
        assert copy.branch_id == 'branch1'
        assert copy.barcode == 'BAR123456'
        assert copy.location == 'A1-B2'
        assert copy.status == CopyStatus.AVAILABLE.value
        assert copy.acquisition_date == datetime.date.today()
        mock_event_bus.add_event.assert_called_once()

    def test_create_copy_with_acquisition_date(self, mock_event_bus: object) -> None:
        past_date = datetime.date(2020, 1, 1)
        copy = Copy.create(item_id='item1', branch_id='branch1', barcode='BAR123456', acquisition_date=past_date)

        assert copy.acquisition_date == past_date

    def test_is_older_version(self, mock_event_bus: object) -> None:
        old_date = datetime.date.today() - datetime.timedelta(days=365 * 3)
        copy = Copy(id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', acquisition_date=old_date)

        assert copy.is_older_version() is True

    def test_is_not_older_version(self, mock_event_bus: object) -> None:
        recent_date = datetime.date.today() - datetime.timedelta(days=365)
        copy = Copy(id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', acquisition_date=recent_date)

        assert copy.is_older_version() is False

    def test_mark_as_checked_out(self, mock_event_bus: object) -> None:
        copy = Copy(
            id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', status=CopyStatus.AVAILABLE.value
        )

        copy.mark_as_checked_out()

        assert copy.status == CopyStatus.CHECKED_OUT.value

    def test_mark_as_checked_out_not_available(self, mock_event_bus: object) -> None:
        copy = Copy(
            id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', status=CopyStatus.CHECKED_OUT.value
        )

        with pytest.raises(CopyNotAvailable):
            copy.mark_as_checked_out()

    def test_mark_as_available(self, mock_event_bus: object) -> None:
        copy = Copy(
            id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', status=CopyStatus.CHECKED_OUT.value
        )

        copy.mark_as_available()

        assert copy.status == CopyStatus.AVAILABLE.value

    def test_mark_as_available_not_checked_out(self, mock_event_bus: object) -> None:
        copy = Copy(
            id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', status=CopyStatus.AVAILABLE.value
        )

        with pytest.raises(CopyNotCheckedOut):
            copy.mark_as_available()

    def test_mark_as_lost(self, mock_event_bus: object) -> None:
        copy = Copy(
            id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', status=CopyStatus.CHECKED_OUT.value
        )

        copy.mark_as_lost()

        assert copy.status == CopyStatus.LOST.value

    def test_mark_as_lost_already_lost(self, mock_event_bus: object) -> None:
        copy = Copy(id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', status=CopyStatus.LOST.value)

        with pytest.raises(CopyAlreadyLost):
            copy.mark_as_lost()

    def test_mark_as_damaged(self, mock_event_bus: object) -> None:
        copy = Copy(
            id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', status=CopyStatus.AVAILABLE.value
        )

        copy.mark_as_damaged()

        assert copy.status == CopyStatus.DAMAGED.value

    def test_mark_as_damaged_already_damaged(self, mock_event_bus: object) -> None:
        copy = Copy(
            id='copy1', item_id='item1', branch_id='branch1', barcode='BAR123456', status=CopyStatus.DAMAGED.value
        )

        with pytest.raises(CopyAlreadyDamaged):
            copy.mark_as_damaged()


class TestItem:
    def test_create_item_minimal(self, mock_event_bus: object) -> None:
        item = Item.create(title='Test Book')

        assert item.title == 'Test Book'
        assert item.format == ItemFormat.BOOK.value
        assert item.isbn is None
        assert item.publisher_id is None
        mock_event_bus.add_event.assert_called_once()

    def test_create_item_full(self, mock_event_bus: object) -> None:
        item = Item.create(
            title='Complete Book',
            format=ItemFormat.BOOK.value,
            isbn='978-0-123456-78-9',
            publisher_id='pub1',
            publication_year=2023,
            category_id='cat1',
            edition='2nd Edition',
            description='A comprehensive guide',
        )

        assert item.title == 'Complete Book'
        assert item.isbn == '978-0-123456-78-9'
        assert item.publisher_id == 'pub1'
        assert item.publication_year == 2023
        assert item.category_id == 'cat1'
        assert item.edition == '2nd Edition'
        assert item.description == 'A comprehensive guide'

    def test_create_item_different_formats(self, mock_event_bus: object) -> None:
        dvd = Item.create(title='Test DVD', format=ItemFormat.DVD.value)
        assert dvd.format == ItemFormat.DVD.value

        cd = Item.create(title='Test CD', format=ItemFormat.CD.value)
        assert cd.format == ItemFormat.CD.value

        magazine = Item.create(title='Test Magazine', format=ItemFormat.MAGAZINE.value)
        assert magazine.format == ItemFormat.MAGAZINE.value


class TestAuthor:
    def test_create_author(self, mock_event_bus: object) -> None:
        author = Author.create(name='John Doe', bio='Famous author')

        assert author.name == 'John Doe'
        assert author.bio == 'Famous author'
        mock_event_bus.add_event.assert_called_once()

    def test_create_author_minimal(self, mock_event_bus: object) -> None:
        author = Author.create(name='Jane Smith')

        assert author.name == 'Jane Smith'
        assert author.bio is None


class TestPublisher:
    def test_create_publisher(self, mock_event_bus: object) -> None:
        publisher = Publisher.create(name='Test Publisher')

        assert publisher.name == 'Test Publisher'
        mock_event_bus.add_event.assert_called_once()


class TestCategory:
    def test_create_category(self, mock_event_bus: object) -> None:
        category = Category.create(name='Science Fiction', description='Futuristic stories')

        assert category.name == 'Science Fiction'
        assert category.description == 'Futuristic stories'
        mock_event_bus.add_event.assert_called_once()

    def test_create_category_minimal(self, mock_event_bus: object) -> None:
        category = Category.create(name='History')

        assert category.name == 'History'
        assert category.description is None
