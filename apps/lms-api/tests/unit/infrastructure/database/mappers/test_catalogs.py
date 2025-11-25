"""Unit tests for catalogs mappers - function-based with comprehensive coverage."""

import uuid
from datetime import date

from lms.domain.catalogs.entities import Copy, Item, Author, Category, Publisher
from lms.infrastructure.database.models.catalogs import (
    CopyModel,
    ItemModel,
    CopyStatus,
    ItemFormat,
    AuthorModel,
    CategoryModel,
    PublisherModel,
)
from lms.infrastructure.database.mappers.catalogs import (
    CopyMapper,
    ItemMapper,
    AuthorMapper,
    CategoryMapper,
    PublisherMapper,
)


# CopyMapper Tests
def test_copy_mapper_to_entity_with_id() -> None:
    model = CopyModel()
    model.id = uuid.uuid4()
    model.item_id = uuid.uuid4()
    model.branch_id = uuid.uuid4()
    model.barcode = 'BC123456'
    model.status = CopyStatus.AVAILABLE
    model.location = 'Shelf A1'
    model.acquisition_date = date(2024, 1, 15)

    entity = CopyMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.item_id == str(model.item_id)
    assert entity.branch_id == str(model.branch_id)
    assert entity.barcode == 'BC123456'
    assert entity.status == 'available'
    assert entity.location == 'Shelf A1'
    assert entity.acquisition_date == date(2024, 1, 15)


def test_copy_mapper_to_entity_without_id() -> None:
    model = CopyModel()
    model.id = None
    model.item_id = uuid.uuid4()
    model.branch_id = uuid.uuid4()
    model.barcode = 'BC123456'
    model.status = CopyStatus.AVAILABLE
    model.location = 'Shelf A1'
    model.acquisition_date = date(2024, 1, 15)

    entity = CopyMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.status == 'available'


def test_copy_mapper_from_entity_with_id() -> None:
    entity = Copy(
        id=str(uuid.uuid4()),
        item_id=str(uuid.uuid4()),
        branch_id=str(uuid.uuid4()),
        barcode='BC123456',
        status='available',
        location='Shelf A1',
        acquisition_date=date(2024, 1, 15),
    )

    model = CopyMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert str(model.item_id) == entity.item_id
    assert str(model.branch_id) == entity.branch_id
    assert model.barcode == 'BC123456'
    assert model.status == CopyStatus.AVAILABLE
    assert model.location == 'Shelf A1'
    assert model.acquisition_date == date(2024, 1, 15)


def test_copy_mapper_from_entity_without_id() -> None:
    entity = Copy(
        id=None,
        item_id=str(uuid.uuid4()),
        branch_id=str(uuid.uuid4()),
        barcode='BC123456',
        status='damaged',
        location='Shelf A1',
        acquisition_date=date(2024, 1, 15),
    )

    model = CopyMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.status == CopyStatus.DAMAGED


# ItemMapper Tests
def test_item_mapper_to_entity_with_all_fields() -> None:
    model = ItemModel()
    model.id = uuid.uuid4()
    model.title = 'Test Book'
    model.isbn = '978-0-123456-78-9'
    model.publisher_id = uuid.uuid4()
    model.publication_year = 2023
    model.category_id = uuid.uuid4()
    model.edition = '1st'
    model.format = ItemFormat.BOOK
    model.description = 'A test book'

    entity = ItemMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.title == 'Test Book'
    assert entity.isbn == '978-0-123456-78-9'
    assert entity.publisher_id == str(model.publisher_id)
    assert entity.publication_year == 2023
    assert entity.category_id == str(model.category_id)
    assert entity.edition == '1st'
    assert entity.format == 'book'
    assert entity.description == 'A test book'


def test_item_mapper_to_entity_with_optional_fields_none() -> None:
    model = ItemModel()
    model.id = uuid.uuid4()
    model.title = 'Test Book'
    model.isbn = '978-0-123456-78-9'
    model.publisher_id = None
    model.publication_year = 2023
    model.category_id = None
    model.edition = '1st'
    model.format = ItemFormat.EBOOK
    model.description = 'A test book'

    entity = ItemMapper.to_entity(model)

    assert entity.publisher_id is None
    assert entity.category_id is None
    assert entity.format == 'ebook'


def test_item_mapper_to_entity_without_id() -> None:
    model = ItemModel()
    model.id = None
    model.title = 'Test Book'
    model.isbn = '978-0-123456-78-9'
    model.publisher_id = uuid.uuid4()
    model.publication_year = 2023
    model.category_id = uuid.uuid4()
    model.edition = '1st'
    model.format = ItemFormat.DVD
    model.description = 'A test book'

    entity = ItemMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.format == 'dvd'


def test_item_mapper_from_entity_with_all_fields() -> None:
    entity = Item(
        id=str(uuid.uuid4()),
        title='Test Book',
        isbn='978-0-123456-78-9',
        publisher_id=str(uuid.uuid4()),
        publication_year=2023,
        category_id=str(uuid.uuid4()),
        edition='1st',
        format='book',
        description='A test book',
    )

    model = ItemMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.title == 'Test Book'
    assert model.isbn == '978-0-123456-78-9'
    assert str(model.publisher_id) == entity.publisher_id
    assert model.publication_year == 2023
    assert str(model.category_id) == entity.category_id
    assert model.edition == '1st'
    assert model.format == ItemFormat.BOOK
    assert model.description == 'A test book'


def test_item_mapper_from_entity_with_optional_fields_none() -> None:
    entity = Item(
        id=str(uuid.uuid4()),
        title='Test Book',
        isbn='978-0-123456-78-9',
        publisher_id=None,
        publication_year=2023,
        category_id=None,
        edition='1st',
        format='ebook',
        description='A test book',
    )

    model = ItemMapper.from_entity(entity)

    assert model.publisher_id is None
    assert model.category_id is None
    assert model.format == ItemFormat.EBOOK


def test_item_mapper_from_entity_without_id() -> None:
    entity = Item(
        id=None,
        title='Test Book',
        isbn='978-0-123456-78-9',
        publisher_id=str(uuid.uuid4()),
        publication_year=2023,
        category_id=str(uuid.uuid4()),
        edition='1st',
        format='magazine',
        description='A test book',
    )

    model = ItemMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.format == ItemFormat.MAGAZINE


# CategoryMapper Tests
def test_category_mapper_to_entity_with_id() -> None:
    model = CategoryModel()
    model.id = uuid.uuid4()
    model.name = 'Fiction'
    model.description = 'Fiction books'

    entity = CategoryMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.name == 'Fiction'
    assert entity.description == 'Fiction books'


def test_category_mapper_to_entity_without_id() -> None:
    model = CategoryModel()
    model.id = None
    model.name = 'Non-Fiction'
    model.description = 'Non-fiction books'

    entity = CategoryMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.name == 'Non-Fiction'


def test_category_mapper_from_entity_with_id() -> None:
    entity = Category(id=str(uuid.uuid4()), name='Science', description='Science books')

    model = CategoryMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.name == 'Science'
    assert model.description == 'Science books'


def test_category_mapper_from_entity_without_id() -> None:
    entity = Category(id=None, name='History', description='History books')

    model = CategoryMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.name == 'History'


# AuthorMapper Tests
def test_author_mapper_to_entity_with_id() -> None:
    model = AuthorModel()
    model.id = uuid.uuid4()
    model.name = 'John Doe'
    model.bio = 'Famous author'
    model.birth_date = date(1980, 5, 15)

    entity = AuthorMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.name == 'John Doe'
    assert entity.bio == 'Famous author'
    assert entity.birth_date == date(1980, 5, 15)


def test_author_mapper_to_entity_without_id() -> None:
    model = AuthorModel()
    model.id = None
    model.name = 'Jane Smith'
    model.bio = 'Bestselling author'
    model.birth_date = date(1975, 3, 20)

    entity = AuthorMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.name == 'Jane Smith'


def test_author_mapper_from_entity_with_id() -> None:
    entity = Author(id=str(uuid.uuid4()), name='John Doe', bio='Famous author', birth_date=date(1980, 5, 15))

    model = AuthorMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.name == 'John Doe'
    assert model.bio == 'Famous author'
    assert model.birth_date == date(1980, 5, 15)


def test_author_mapper_from_entity_without_id() -> None:
    entity = Author(id=None, name='Jane Smith', bio='Bestselling author', birth_date=date(1975, 3, 20))

    model = AuthorMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.name == 'Jane Smith'


# PublisherMapper Tests
def test_publisher_mapper_to_entity_with_id() -> None:
    model = PublisherModel()
    model.id = uuid.uuid4()
    model.name = 'Test Publisher'
    model.address = '123 Publisher St'

    entity = PublisherMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.name == 'Test Publisher'
    assert entity.address == '123 Publisher St'


def test_publisher_mapper_to_entity_without_id() -> None:
    model = PublisherModel()
    model.id = None
    model.name = 'Another Publisher'
    model.address = '456 Book Ave'

    entity = PublisherMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.name == 'Another Publisher'


def test_publisher_mapper_from_entity_with_id() -> None:
    entity = Publisher(id=str(uuid.uuid4()), name='Test Publisher', address='123 Publisher St')

    model = PublisherMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.name == 'Test Publisher'
    assert model.address == '123 Publisher St'


def test_publisher_mapper_from_entity_without_id() -> None:
    entity = Publisher(id=None, name='Another Publisher', address='456 Book Ave')

    model = PublisherMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.name == 'Another Publisher'
