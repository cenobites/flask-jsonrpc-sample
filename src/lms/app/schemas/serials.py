from __future__ import annotations

from pydantic import Field

from . import BaseSchema


class SerialCreate(BaseSchema):
    title: str = Field(min_length=1, max_length=255, description='Serial publication title')
    issn: str = Field(min_length=1, max_length=30, description='ISSN number')
    item_id: str = Field(description='Catalog item ID associated with the serial')
    frequency: str | None = Field(None, max_length=50, description='Publication frequency')
    description: str | None = Field(None, max_length=1000, description='Serial description')
