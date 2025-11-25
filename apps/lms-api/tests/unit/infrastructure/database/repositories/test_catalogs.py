"""Unit tests for catalogs repositories - function-based with 100% coverage."""

from datetime import date
from unittest.mock import Mock, patch

import pytest
import sqlalchemy.exc as sa_exc

from tests.unit.factories import CopyFactory, ItemFactory, AuthorFactory, CategoryFactory, PublisherFactory
from lms.infrastructure.database import RepositoryError
from lms.infrastructure.database.repositories.catalogs import (
    SQLAlchemyCopyRepository,
    SQLAlchemyItemRepository,
    SQLAlchemyAuthorRepository,
    SQLAlchemyCategoryRepository,
    SQLAlchemyPublisherRepository,
)


# Fixtures
@pytest.fixture
def mock_session() -> Mock:
    return Mock()


# SQLAlchemyCopyRepository Tests
def test_copy_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_copy1 = CopyFactory.build()
    mock_copy2 = CopyFactory.build()
    mock_session.query.return_value.all.return_value = [mock_copy1, mock_copy2]

    with patch('lms.infrastructure.database.repositories.catalogs.CopyMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        copies = repo.find_all()

        assert len(copies) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_copy_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to retrieve copies'):
        repo.find_all()


def test_copy_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_copy = CopyFactory.build()
    mock_session.get.return_value = mock_copy

    with patch('lms.infrastructure.database.repositories.catalogs.CopyMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_copy
        copy = repo.get_by_id('copy1')

        assert copy == mock_copy
        mock_session.get.assert_called_once()


def test_copy_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_session.get.return_value = None

    copy = repo.get_by_id('nonexistent')

    assert copy is None


def test_copy_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve copy'):
        repo.get_by_id('copy1')


def test_copy_save_new_copy(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_copy = Mock()
    mock_copy.id = None
    mock_model = CopyFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.catalogs.CopyMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_copy)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert mock_copy.id == str(mock_model.id)


def test_copy_save_new_copy_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_copy = Mock()
    mock_copy.id = None
    mock_model = CopyFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.catalogs.CopyMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save copy'):
            repo.save(mock_copy)

        mock_session.rollback.assert_called_once()


def test_copy_save_existing_copy(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_copy = Mock()
    mock_copy.id = 'copy1'
    mock_copy.status = 'available'

    mock_model = Mock()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_copy)

    # Check that status was set (the CopyStatus enum call)
    mock_session.commit.assert_called_once()
    assert result == mock_copy


def test_copy_save_existing_copy_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_copy = Mock()
    mock_copy.id = 'copy1'
    mock_copy.status = 'available'

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to save copy'):
        repo.save(mock_copy)

    mock_session.rollback.assert_called_once()


def test_copy_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)

    repo.delete_by_id('copy1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_copy_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCopyRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete copy'):
        repo.delete_by_id('copy1')

    mock_session.rollback.assert_called_once()


# SQLAlchemyItemRepository Tests
def test_item_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_item1 = ItemFactory.build()
    mock_item2 = ItemFactory.build()
    mock_session.query.return_value.all.return_value = [mock_item1, mock_item2]

    with patch('lms.infrastructure.database.repositories.catalogs.ItemMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        items = repo.find_all()

        assert len(items) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_item_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve items'):
        repo.find_all()


def test_item_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_item = ItemFactory.build()
    mock_session.get.return_value = mock_item

    with patch('lms.infrastructure.database.repositories.catalogs.ItemMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_item
        item = repo.get_by_id('item1')

        assert item == mock_item


def test_item_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_session.get.return_value = None

    item = repo.get_by_id('nonexistent')

    assert item is None


def test_item_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve item'):
        repo.get_by_id('item1')


def test_item_exists_by_title_returns_true(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value = Mock()
    mock_session.query.return_value.exists.return_value = Mock()
    mock_session.query.return_value.scalar.return_value = True

    result = repo.exists_by_title('Test Title')

    assert result is True


def test_item_exists_by_title_returns_false(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value = Mock()
    mock_session.query.return_value.exists.return_value = Mock()
    mock_session.query.return_value.scalar.return_value = False

    result = repo.exists_by_title('Test Title')

    assert result is False


def test_item_exists_by_title_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to check item existence by title'):
        repo.exists_by_title('Test Title')


def test_item_save_new_item(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_item = Mock()
    mock_item.id = None
    mock_model = ItemFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.catalogs.ItemMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_item)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()


def test_item_save_new_item_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_item = Mock()
    mock_item.id = None
    mock_model = ItemFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.catalogs.ItemMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save item'):
            repo.save(mock_item)

        mock_session.rollback.assert_called_once()


def test_item_save_existing_item(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_item = Mock(
        id='item1', title='Updated Title', isbn='9876543210', publication_year=2024, edition=2, description='Updated'
    )
    mock_model = Mock()

    mock_session.get.return_value = mock_model
    repo.save(mock_item)

    assert mock_model.title == 'Updated Title'
    assert mock_model.isbn == '9876543210'
    assert mock_model.publication_year == 2024
    assert mock_model.edition == 2
    assert mock_model.description == 'Updated'
    mock_session.commit.assert_called_once()


def test_item_save_existing_item_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_item = Mock(id='item1', title='Updated', isbn='123', publication_year=2024, edition=2, description='Test')
    mock_model = Mock()

    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to save item'):
        repo.save(mock_item)

    mock_session.rollback.assert_called_once()


def test_item_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)

    repo.delete_by_id('item1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_item_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyItemRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete item'):
        repo.delete_by_id('item1')

    mock_session.rollback.assert_called_once()


# SQLAlchemyAuthorRepository Tests
def test_author_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_author1 = AuthorFactory.build()
    mock_author2 = AuthorFactory.build()
    mock_session.query.return_value.all.return_value = [mock_author1, mock_author2]

    with patch('lms.infrastructure.database.repositories.catalogs.AuthorMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        authors = repo.find_all()

        assert len(authors) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_author_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve authors'):
        repo.find_all()


def test_author_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_author = AuthorFactory.build()
    mock_session.get.return_value = mock_author

    with patch('lms.infrastructure.database.repositories.catalogs.AuthorMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_author
        author = repo.get_by_id('author1')

        assert author == mock_author


def test_author_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_session.get.return_value = None

    author = repo.get_by_id('nonexistent')

    assert author is None


def test_author_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve author'):
        repo.get_by_id('author1')


def test_author_save_new_author(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_author = Mock()
    mock_author.id = None
    mock_model = AuthorFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.catalogs.AuthorMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_author)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


def test_author_save_new_author_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_author = Mock()
    mock_author.id = None
    mock_model = AuthorFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.catalogs.AuthorMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save author'):
            repo.save(mock_author)

        mock_session.rollback.assert_called_once()


def test_author_save_existing_author(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_author = Mock()
    mock_author.id = 'author1'
    mock_author.name = 'Updated Name'
    mock_author.bio = 'Updated Bio'
    mock_author.birth_date = date(1980, 1, 1)
    mock_model = Mock()

    mock_session.get.return_value = mock_model
    result = repo.save(mock_author)

    assert mock_model.name == 'Updated Name'
    assert mock_model.bio == 'Updated Bio'
    assert mock_model.birth_date == date(1980, 1, 1)
    mock_session.commit.assert_called_once()
    assert result == mock_author


def test_author_save_existing_author_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_author = Mock(id='author1', name='Updated', bio='Bio', birth_date=date(1980, 1, 1))
    mock_model = Mock()

    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to save author'):
        repo.save(mock_author)

    mock_session.rollback.assert_called_once()


def test_author_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)

    repo.delete_by_id('author1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_author_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAuthorRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete author'):
        repo.delete_by_id('author1')

    mock_session.rollback.assert_called_once()


# SQLAlchemyPublisherRepository Tests
def test_publisher_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_pub1 = PublisherFactory.build()
    mock_pub2 = PublisherFactory.build()
    mock_session.query.return_value.all.return_value = [mock_pub1, mock_pub2]

    with patch('lms.infrastructure.database.repositories.catalogs.PublisherMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        publishers = repo.find_all()

        assert len(publishers) == 2


def test_publisher_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve publishers'):
        repo.find_all()


def test_publisher_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_publisher = PublisherFactory.build()
    mock_session.get.return_value = mock_publisher

    with patch('lms.infrastructure.database.repositories.catalogs.PublisherMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_publisher
        publisher = repo.get_by_id('pub1')

        assert publisher == mock_publisher


def test_publisher_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_session.get.return_value = None

    publisher = repo.get_by_id('nonexistent')

    assert publisher is None


def test_publisher_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve publisher'):
        repo.get_by_id('pub1')


def test_publisher_save_new_publisher(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_publisher = Mock()
    mock_publisher.id = None
    mock_model = PublisherFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.catalogs.PublisherMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_publisher)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


def test_publisher_save_new_publisher_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_publisher = Mock()
    mock_publisher.id = None
    mock_model = PublisherFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.catalogs.PublisherMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save publisher'):
            repo.save(mock_publisher)

        mock_session.rollback.assert_called_once()


def test_publisher_save_existing_publisher(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_publisher = Mock()
    mock_publisher.id = 'pub1'
    mock_publisher.name = 'Updated Name'
    mock_publisher.address = 'New Address'
    mock_publisher.email = 'new@pub.com'
    mock_model = Mock()

    mock_session.get.return_value = mock_model
    result = repo.save(mock_publisher)

    assert mock_model.name == 'Updated Name'
    assert mock_model.address == 'New Address'
    assert mock_model.email == 'new@pub.com'
    mock_session.commit.assert_called_once()
    assert result == mock_publisher


def test_publisher_save_existing_publisher_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_publisher = Mock(id='pub1', name='Updated', address='Address', email='email@pub.com')
    mock_model = Mock()

    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to save publisher'):
        repo.save(mock_publisher)

    mock_session.rollback.assert_called_once()


def test_publisher_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)

    repo.delete_by_id('pub1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_publisher_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyPublisherRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete publisher'):
        repo.delete_by_id('pub1')

    mock_session.rollback.assert_called_once()


# SQLAlchemyCategoryRepository Tests
def test_category_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_cat1 = CategoryFactory.build()
    mock_cat2 = CategoryFactory.build()
    mock_session.query.return_value.all.return_value = [mock_cat1, mock_cat2]

    with patch('lms.infrastructure.database.repositories.catalogs.CategoryMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        categories = repo.find_all()

        assert len(categories) == 2


def test_category_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve categories'):
        repo.find_all()


def test_category_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_category = CategoryFactory.build()
    mock_session.get.return_value = mock_category

    with patch('lms.infrastructure.database.repositories.catalogs.CategoryMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_category
        category = repo.get_by_id('cat1')

        assert category == mock_category


def test_category_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_session.get.return_value = None

    category = repo.get_by_id('nonexistent')

    assert category is None


def test_category_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve category'):
        repo.get_by_id('cat1')


def test_category_save_new_category(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_category = Mock()
    mock_category.id = None
    mock_model = CategoryFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.catalogs.CategoryMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        repo.save(mock_category)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()


def test_category_save_new_category_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_category = Mock()
    mock_category.id = None
    mock_model = CategoryFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.catalogs.CategoryMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save category'):
            repo.save(mock_category)

        mock_session.rollback.assert_called_once()


def test_category_save_existing_category(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_category = Mock()
    mock_category.id = 'cat1'
    mock_category.name = 'Updated Category'
    mock_category.description = 'Updated Description'
    mock_model = Mock()

    mock_session.get.return_value = mock_model
    result = repo.save(mock_category)

    assert mock_model.name == 'Updated Category'
    assert mock_model.description == 'Updated Description'
    mock_session.commit.assert_called_once()
    assert result == mock_category


def test_category_save_existing_category_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_category = Mock(id='cat1', name='Updated', description='Description')
    mock_model = Mock()

    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to save category'):
        repo.save(mock_category)

    mock_session.rollback.assert_called_once()


def test_category_delete_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)

    repo.delete_by_id('cat1')

    mock_session.query.return_value.filter_by.return_value.delete.assert_called_once()
    mock_session.commit.assert_called_once()


def test_category_delete_by_id_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyCategoryRepository(session=mock_session)
    mock_session.query.return_value.filter_by.return_value.delete.side_effect = sa_exc.SQLAlchemyError('DB error')

    with pytest.raises(RepositoryError, match='Failed to delete category'):
        repo.delete_by_id('cat1')

    mock_session.rollback.assert_called_once()
