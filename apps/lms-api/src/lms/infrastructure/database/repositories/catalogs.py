from __future__ import annotations

import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.infrastructure.database import RepositoryError
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
        try:
            models = self.session.query(CopyModel).all()
            return [CopyMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve copies', cause=e) from e

    def get_by_id(self, copy_id: str) -> Copy | None:
        try:
            model = self.session.get(CopyModel, copy_id)
            return CopyMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve copy', cause=e) from e

    def save(self, copy: Copy) -> Copy:
        model = self.session.get(CopyModel, copy.id) if copy.id else None
        if not model:
            model = CopyMapper.from_entity(copy)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save copy', cause=e) from e
            copy.id = str(model.id)
            return copy
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to save copy', cause=e) from e
        return copy

    def delete_by_id(self, copy_id: str) -> None:
        try:
            self.session.query(CopyModel).filter_by(id=copy_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete copy', cause=e) from e


class SQLAlchemyItemRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Item]:
        try:
            models = self.session.query(ItemModel).all()
            return [ItemMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve items', cause=e) from e

    def get_by_id(self, item_id: str) -> Item | None:
        try:
            model = self.session.get(ItemModel, item_id)
            return ItemMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve item', cause=e) from e

    def exists_by_title(self, title: str) -> bool:
        try:
            q = self.session.query(ItemModel).filter_by(title=title)
            count = self.session.query(q.exists()).scalar()
            return count is not None and count > 0
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to check item existence by title', cause=e) from e

    def save(self, item: Item) -> Item:
        model = self.session.get(ItemModel, item.id) if item.id else None
        if not model:
            model = ItemMapper.from_entity(item)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save item', cause=e) from e
            item.id = str(model.id)
            return item
        model.title = item.title
        model.isbn = item.isbn
        model.publication_year = item.publication_year
        model.edition = item.edition
        model.description = item.description
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to save item', cause=e) from e
        return item

    def delete_by_id(self, item_id: str) -> None:
        try:
            self.session.query(ItemModel).filter_by(id=item_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete item', cause=e) from e


class SQLAlchemyCategoryRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Category]:
        try:
            models = self.session.query(CategoryModel).all()
            return [CategoryMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve categories', cause=e) from e

    def get_by_id(self, category_id: str) -> Category | None:
        try:
            model = self.session.get(CategoryModel, category_id)
            return CategoryMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve category', cause=e) from e

    def save(self, category: Category) -> Category:
        model = self.session.get(CategoryModel, category.id)
        if not model:
            model = CategoryMapper.from_entity(category)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save category', cause=e) from e
            category.id = str(model.id)
            return category
        model.name = category.name
        model.description = category.description
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to save category', cause=e) from e
        return category

    def delete_by_id(self, category_id: str) -> None:
        try:
            self.session.query(CategoryModel).filter_by(id=category_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete category', cause=e) from e


class SQLAlchemyAuthorRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Author]:
        try:
            models = self.session.query(AuthorModel).all()
            return [AuthorMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve authors', cause=e) from e

    def get_by_id(self, author_id: str) -> Author | None:
        try:
            model = self.session.get(AuthorModel, author_id)
            return AuthorMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve author', cause=e) from e

    def save(self, author: Author) -> Author:
        model = self.session.get(AuthorModel, author.id) if author.id else None
        if not model:
            model = AuthorMapper.from_entity(author)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save author', cause=e) from e
            author.id = str(model.id)
            return author
        model.name = author.name
        model.bio = author.bio
        model.birth_date = author.birth_date
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to save author', cause=e) from e
        return author

    def delete_by_id(self, author_id: str) -> None:
        try:
            self.session.query(AuthorModel).filter_by(id=author_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete author', cause=e) from e


class SQLAlchemyPublisherRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Publisher]:
        try:
            models = self.session.query(PublisherModel).all()
            return [PublisherMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve publishers', cause=e) from e

    def get_by_id(self, publisher_id: str) -> Publisher | None:
        try:
            model = self.session.get(PublisherModel, publisher_id)
            return PublisherMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve publisher', cause=e) from e

    def save(self, publisher: Publisher) -> Publisher:
        model = self.session.get(PublisherModel, publisher.id) if publisher.id else None
        if not model:
            model = PublisherMapper.from_entity(publisher)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save publisher', cause=e) from e
            publisher.id = str(model.id)
            return publisher
        model.name = publisher.name
        model.address = publisher.address
        model.email = publisher.email
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to save publisher', cause=e) from e
        return publisher

    def delete_by_id(self, publisher_id: str) -> None:
        try:
            self.session.query(PublisherModel).filter_by(id=publisher_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete publisher', cause=e) from e
