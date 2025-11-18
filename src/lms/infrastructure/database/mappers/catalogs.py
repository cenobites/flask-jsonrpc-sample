from __future__ import annotations

import uuid

from lms.domain.catalogs.entities import Copy, Item, Author, Category, Publisher

from ..models.catalogs import CopyModel, ItemModel, CopyStatus, ItemFormat, AuthorModel, CategoryModel, PublisherModel


class CopyMapper:
    @staticmethod
    def to_entity(model: CopyModel) -> Copy:
        return Copy(
            id=str(model.id) if model.id else None,
            item_id=str(model.item_id),
            branch_id=str(model.branch_id),
            barcode=model.barcode,
            status=model.status.value,
            location=model.location,
            acquisition_date=model.acquisition_date,
        )

    @staticmethod
    def from_entity(entity: Copy) -> CopyModel:
        model = CopyModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.item_id = uuid.UUID(entity.item_id)
        model.branch_id = uuid.UUID(entity.branch_id)
        model.barcode = entity.barcode
        model.status = CopyStatus(entity.status)
        model.location = entity.location
        model.acquisition_date = entity.acquisition_date
        return model


class ItemMapper:
    @staticmethod
    def to_entity(model: ItemModel) -> Item:
        return Item(
            id=str(model.id) if model.id else None,
            title=model.title,
            isbn=model.isbn,
            publisher_id=str(model.publisher_id) if model.publisher_id else None,
            publication_year=model.publication_year,
            category_id=str(model.category_id) if model.category_id else None,
            edition=model.edition,
            format=model.format.value,
            description=model.description,
        )

    @staticmethod
    def from_entity(entity: Item) -> ItemModel:
        model = ItemModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.title = entity.title
        model.isbn = entity.isbn
        model.publisher_id = uuid.UUID(entity.publisher_id) if entity.publisher_id else None
        model.publication_year = entity.publication_year
        model.category_id = uuid.UUID(entity.category_id) if entity.category_id else None
        model.edition = entity.edition
        model.format = ItemFormat(entity.format)
        model.description = entity.description
        return model


class CategoryMapper:
    @staticmethod
    def to_entity(model: CategoryModel) -> Category:
        return Category(id=str(model.id) if model.id else None, name=model.name, description=model.description)

    @staticmethod
    def from_entity(entity: Category) -> CategoryModel:
        model = CategoryModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.name = entity.name
        model.description = entity.description
        return model


class AuthorMapper:
    @staticmethod
    def to_entity(model: AuthorModel) -> Author:
        return Author(
            id=str(model.id) if model.id else None, name=model.name, bio=model.bio, birth_date=model.birth_date
        )

    @staticmethod
    def from_entity(entity: Author) -> AuthorModel:
        model = AuthorModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.name = entity.name
        model.bio = entity.bio
        model.birth_date = entity.birth_date
        return model


class PublisherMapper:
    @staticmethod
    def to_entity(model: PublisherModel) -> Publisher:
        return Publisher(id=str(model.id) if model.id else None, name=model.name, address=model.address)

    @staticmethod
    def from_entity(entity: Publisher) -> PublisherModel:
        model = PublisherModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.name = entity.name
        model.address = entity.address
        return model
