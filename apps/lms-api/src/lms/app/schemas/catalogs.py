from __future__ import annotations

from pydantic import Field

from lms.infrastructure.database.models.catalogs import ItemFormat

from . import BaseSchema


class ItemCreate(BaseSchema):
    title: str = Field(description='Title of the catalog item')
    isbn: str | None = Field(default=None, description='ISBN number of the item')
    publisher_id: str | None = Field(default=None, description='ID of the publisher')
    publication_year: int | None = Field(default=None, description='Year the item was published')
    category_id: str | None = Field(default=None, description='ID of the item category')
    edition: str | None = Field(default=None, description='Edition of the item')
    format: ItemFormat = Field(default=ItemFormat.BOOK, description='Format of the catalog item')
    description: str | None = Field(default=None, description='Description of the catalog item')


class ItemUpdate(BaseSchema):
    id: str = Field(description='Unique item identifier')
    title: str = Field(description='Title of the catalog item')
    isbn: str | None = Field(default=None, description='ISBN number of the item')
    publisher_id: str | None = Field(default=None, description='ID of the publisher')
    publication_year: int | None = Field(default=None, description='Year the item was published')
    category_id: str | None = Field(default=None, description='ID of the item category')
    edition: str | None = Field(default=None, description='Edition of the item')
    format: ItemFormat = Field(default=ItemFormat.BOOK, description='Format of the catalog item')
    description: str | None = Field(default=None, description='Description of the catalog item')
