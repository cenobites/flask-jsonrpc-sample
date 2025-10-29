from __future__ import annotations

from pydantic import Field

from lms.infrastructure.database.models.catalogs import ItemFormat

from . import BaseSchema


class ItemSchema(BaseSchema):
    barcode: str = Field(..., min_length=3, max_length=50, description='Unique item barcode')
    title: str = Field(..., min_length=1, max_length=500, description='Item title')
    author: str | None = Field(None, max_length=255, description='Item author')
    publisher: str | None = Field(None, max_length=255, description='Publisher name')
    publication_year: int | None = Field(None, ge=1000, le=9999, description='Publication year')
    isbn: str | None = Field(None, max_length=20, description='ISBN number')
    issn: str | None = Field(None, max_length=20, description='ISSN number')
    material_type: ItemFormat = Field(..., description='Type of material')
    location: str | None = Field(None, max_length=100, description='Physical location')
    call_number: str | None = Field(None, max_length=100, description='Library call number')
    price: float | None = Field(None, ge=0, description='Item price')
    description: str | None = Field(None, description='Item description')


class ItemCreate(ItemSchema):
    pass


class ItemUpdate(ItemSchema):
    id: str = Field(description='Unique item identifier')


class CopySchema(BaseSchema):
    barcode: str = Field(..., min_length=3, max_length=50, description='Unique copy barcode')
    branch_id: str = Field(..., gt=0, description='Branch where copy is located')


class CopyCreate(CopySchema):
    pass


class CopyUpdate(CopySchema):
    id: str = Field(description='Unique copy identifier')
