from __future__ import annotations

import datetime
from unittest.mock import Mock, MagicMock

import pytest

from lms.app.services.catalogs import CopyService, ItemService, AuthorService, CategoryService, PublisherService
from lms.domain.catalogs.entities import Copy, Item, Author, Category


@pytest.fixture
def mock_copy_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_item_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_author_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_category_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_publisher_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def copy_service(mock_copy_repository: Mock) -> CopyService:
    return CopyService(copy_repository=mock_copy_repository)


@pytest.fixture
def item_service(mock_item_repository: Mock, mock_copy_repository: Mock) -> ItemService:
    return ItemService(item_repository=mock_item_repository, copy_repository=mock_copy_repository)


@pytest.fixture
def author_service(mock_author_repository: Mock) -> AuthorService:
    return AuthorService(author_repository=mock_author_repository)


@pytest.fixture
def category_service(mock_category_repository: Mock) -> CategoryService:
    return CategoryService(category_repository=mock_category_repository)


@pytest.fixture
def publisher_service(mock_publisher_repository: Mock) -> PublisherService:
    return PublisherService(publisher_repository=mock_publisher_repository)


def test_copy_service_create_copy(copy_service: CopyService, mock_copy_repository: Mock) -> None:
    copy = Mock(spec=Copy)
    mock_copy_repository.save.return_value = copy

    result = copy_service.create_copy(item_id='item-123', branch_id='branch-456', barcode='BC12345')

    assert result == copy
    mock_copy_repository.save.assert_called_once()


def test_copy_service_get_copy_success(copy_service: CopyService, mock_copy_repository: Mock) -> None:
    copy = Mock(spec=Copy, id='copy-123')
    mock_copy_repository.get_by_id.return_value = copy

    result = copy_service.get_copy('copy-123')

    assert result == copy


def test_copy_service_get_copy_not_found(copy_service: CopyService, mock_copy_repository: Mock) -> None:
    mock_copy_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Copy with id copy-999 not found'):
        copy_service.get_copy('copy-999')


def test_copy_service_get_all_copies(copy_service: CopyService, mock_copy_repository: Mock) -> None:
    copies = [Mock(spec=Copy), Mock(spec=Copy)]
    mock_copy_repository.find_all.return_value = copies

    result = copy_service.get_all_copies()

    assert result == copies


def test_copy_service_update_copy_status(copy_service: CopyService, mock_copy_repository: Mock) -> None:
    copy = Mock(spec=Copy)
    copy.id = 'copy-123'
    copy.status = 'available'
    copy.item_id = 'item-1'
    copy.branch_id = 'branch-1'
    copy.barcode = 'BC123'
    copy.location = None
    copy.acquisition_date = None
    mock_copy_repository.get_by_id.return_value = copy
    mock_copy_repository.save.return_value = copy

    result = copy_service.update_copy_status('copy-123', 'checked_out')

    assert result == copy
    mock_copy_repository.save.assert_called_once()


def test_copy_service_delete_copy(copy_service: CopyService, mock_copy_repository: Mock) -> None:
    result = copy_service.delete_copy('copy-123')

    assert result is True
    mock_copy_repository.delete_by_id.assert_called_once_with('copy-123')


def test_item_service_get_all_items(item_service: ItemService, mock_item_repository: Mock) -> None:
    items = [Mock(spec=Item), Mock(spec=Item)]
    mock_item_repository.find_all.return_value = items

    result = item_service.get_all_items()

    assert result == items


def test_item_service_get_item_success(item_service: ItemService, mock_item_repository: Mock) -> None:
    item = Mock(spec=Item, id='item-123')
    mock_item_repository.get_by_id.return_value = item

    result = item_service.get_item('item-123')

    assert result == item


def test_item_service_get_item_not_found(item_service: ItemService, mock_item_repository: Mock) -> None:
    mock_item_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Item with id item-999 not found'):
        item_service.get_item('item-999')


def test_item_service_create_item(item_service: ItemService, mock_item_repository: Mock) -> None:
    item = Mock(spec=Item)
    mock_item_repository.save.return_value = item

    result = item_service.create_item(title='Test Book', format='book')

    assert result == item
    mock_item_repository.save.assert_called_once()


def test_item_service_add_copy_to_item(
    item_service: ItemService, mock_item_repository: Mock, mock_copy_repository: Mock
) -> None:
    item = Mock(spec=Item, id='item-123')
    copy = Mock(spec=Copy)
    mock_item_repository.get_by_id.return_value = item
    mock_copy_repository.save.return_value = copy

    result = item_service.add_copy_to_item(
        item_id='item-123', branch_id='branch-456', barcode='BC123', acquisition_date=datetime.date.today()
    )

    assert result == copy
    mock_copy_repository.save.assert_called_once()


def test_item_service_update_item(item_service: ItemService, mock_item_repository: Mock) -> None:
    item = Mock(spec=Item, id='item-123', title='Old Title')
    mock_item_repository.get_by_id.return_value = item
    mock_item_repository.save.return_value = item

    result = item_service.update_item('item-123', title='New Title')

    assert result == item
    assert item.title == 'New Title'


def test_item_service_delete_item(item_service: ItemService, mock_item_repository: Mock) -> None:
    result = item_service.delete_item('item-123')

    assert result is True
    mock_item_repository.delete_by_id.assert_called_once_with('item-123')


def test_category_service_find_all_categories(
    category_service: CategoryService, mock_category_repository: Mock
) -> None:
    categories = [Mock(spec=Category), Mock(spec=Category)]
    mock_category_repository.find_all.return_value = categories

    result = category_service.find_all_categories()

    assert result == categories


def test_category_service_get_category_success(
    category_service: CategoryService, mock_category_repository: Mock
) -> None:
    category = Mock(spec=Category, id='cat-123')
    mock_category_repository.get_by_id.return_value = category

    result = category_service.get_category('cat-123')

    assert result == category


def test_category_service_get_category_not_found(
    category_service: CategoryService, mock_category_repository: Mock
) -> None:
    mock_category_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Category with id cat-999 not found'):
        category_service.get_category('cat-999')


def test_category_service_register_category(category_service: CategoryService, mock_category_repository: Mock) -> None:
    category = Mock(spec=Category)
    mock_category_repository.save.return_value = category

    result = category_service.register_category(name='Fiction', description='Fictional works')

    assert result == category
    mock_category_repository.save.assert_called_once()


def test_category_service_update_category(category_service: CategoryService, mock_category_repository: Mock) -> None:
    category = Mock(spec=Category, id='cat-123', name='Old Name')
    mock_category_repository.get_by_id.return_value = category
    mock_category_repository.save.return_value = category

    result = category_service.update_category('cat-123', name='New Name')

    assert result == category
    assert category.name == 'New Name'


def test_category_service_delete_category(category_service: CategoryService, mock_category_repository: Mock) -> None:
    result = category_service.delete_category('cat-123')

    assert result is True
    mock_category_repository.delete_by_id.assert_called_once_with('cat-123')


def test_author_service_find_all_authors(author_service: AuthorService, mock_author_repository: Mock) -> None:
    authors = [Mock(spec=Author), Mock(spec=Author)]
    mock_author_repository.find_all.return_value = authors

    result = author_service.find_all_authors()

    assert result == authors


def test_author_service_get_author_success(author_service: AuthorService, mock_author_repository: Mock) -> None:
    author = Mock(spec=Author, id='author-123')
    mock_author_repository.get_by_id.return_value = author

    result = author_service.get_author('author-123')

    assert result == author


def test_author_service_register_author(author_service: AuthorService, mock_author_repository: Mock) -> None:
    author = Mock(spec=Author)
    mock_author_repository.save.return_value = author

    result = author_service.register_author(name='J.K. Rowling', bio='British author')

    assert result == author
    mock_author_repository.save.assert_called_once()


def test_author_service_update_author(author_service: AuthorService, mock_author_repository: Mock) -> None:
    author = Mock(spec=Author, id='author-123', name='Old Name')
    mock_author_repository.get_by_id.return_value = author
    mock_author_repository.save.return_value = author

    result = author_service.update_author('author-123', name='New Name')

    assert result == author
    assert author.name == 'New Name'
