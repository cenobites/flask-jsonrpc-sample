from __future__ import annotations

import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.catalogs.entities import Copy, Item, Author, Category, Publisher
from lms.infrastructure.database.models.catalogs import CopyModel, ItemModel, AuthorModel, CategoryModel, PublisherModel
from lms.infrastructure.database.mappers.catalogs import (
    CopyMapper,
    ItemMapper,
    AuthorMapper,
    CategoryMapper,
    PublisherMapper,
)


class SQLAlchemyCopyRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Copy]:
        models = self.session.query(CopyModel).all()
        return [CopyMapper.to_entity(m) for m in models]

    def get_by_id(self, copy_id: str) -> Copy | None:
        model = self.session.get(CopyModel, copy_id)
        return CopyMapper.to_entity(model) if model else None

    def save(self, copy: Copy) -> Copy:
        model = self.session.get(CopyModel, copy.id) if copy.id else None
        if not model:
            model = CopyMapper.from_entity(copy)
            self.session.add(model)
            self.session.commit()
            copy.id = str(model.id)
            return copy
        self.session.commit()
        return copy

    def delete_by_id(self, copy_id: str) -> None:
        self.session.query(CopyModel).filter_by(id=copy_id).delete()
        self.session.commit()


class SQLAlchemyItemRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Item]:
        models = self.session.query(ItemModel).all()
        return [ItemMapper.to_entity(m) for m in models]

    def get_by_id(self, item_id: str) -> Item | None:
        model = self.session.get(ItemModel, item_id)
        return ItemMapper.to_entity(model) if model else None

    def exists_by_title(self, title: str) -> bool:
        q = self.session.query(ItemModel).filter_by(title=title)
        return self.session.query(q.exists()).scalar()

    def save(self, item: Item) -> Item:
        model = self.session.get(ItemModel, item.id) if item.id else None
        if not model:
            model = ItemMapper.from_entity(item)
            self.session.add(model)
            self.session.commit()
            item.id = str(model.id)
            return item
        item.title = model.title
        item.isbn = model.isbn
        self.session.commit()
        return item

    def delete_by_id(self, item_id: str) -> None:
        self.session.query(ItemModel).filter_by(id=item_id).delete()
        self.session.commit()


class SQLAlchemyCategoryRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Category]:
        models = self.session.query(CategoryModel).all()
        return [CategoryMapper.to_entity(m) for m in models]

    def get_by_id(self, category_id: str) -> Category | None:
        model = self.session.get(CategoryModel, category_id)
        return CategoryMapper.to_entity(model) if model else None

    def save(self, category: Category) -> Category:
        model = self.session.get(CategoryModel, category.id)
        if not model:
            model = CategoryMapper.from_entity(category)
            self.session.add(model)
            self.session.commit()
            category.id = str(model.id)
            return category
        model.name = category.name
        model.description = category.description
        self.session.commit()
        return category

    def delete_by_id(self, category_id: str) -> None:
        self.session.query(CategoryModel).filter_by(id=category_id).delete()
        self.session.commit()


class SQLAlchemyAuthorRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Author]:
        models = self.session.query(AuthorModel).all()
        return [AuthorMapper.to_entity(m) for m in models]

    def get_by_id(self, author_id: str) -> Author | None:
        model = self.session.get(AuthorModel, author_id)
        return AuthorMapper.to_entity(model) if model else None

    def save(self, author: Author) -> Author:
        model = self.session.get(AuthorModel, author.id) if author.id else None
        if not model:
            model = AuthorMapper.from_entity(author)
            self.session.add(model)
            self.session.commit()
            author.id = str(model.id)
            return author
        model.name = author.name
        model.bio = author.bio
        model.birth_date = author.birth_date
        self.session.commit()
        return author

    def delete_by_id(self, author_id: str) -> None:
        self.session.query(AuthorModel).filter_by(id=author_id).delete()
        self.session.commit()


class SQLAlchemyPublisherRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Publisher]:
        models = self.session.query(PublisherModel).all()
        return [PublisherMapper.to_entity(m) for m in models]

    def get_by_id(self, publisher_id: str) -> Publisher | None:
        model = self.session.get(PublisherModel, publisher_id)
        return PublisherMapper.to_entity(model) if model else None

    def save(self, publisher: Publisher) -> Publisher:
        model = self.session.get(PublisherModel, publisher.id) if publisher.id else None
        if not model:
            model = PublisherMapper.from_entity(publisher)
            self.session.add(model)
            self.session.commit()
            publisher.id = str(model.id)
            return publisher
        model.name = publisher.name
        model.address = publisher.address
        model.email = publisher.email
        self.session.commit()
        return publisher

    def delete_by_id(self, publisher_id: str) -> None:
        self.session.query(PublisherModel).filter_by(id=publisher_id).delete()
        self.session.commit()
