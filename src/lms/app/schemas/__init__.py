from __future__ import annotations

import typing as t
from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict

T_Page_Results = t.TypeVar('T_Page_Results')


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class Page[T_Page_Results](BaseSchema):
    results: list[T_Page_Results] = Field(..., description='List of items on the current page')
    count: int = Field(..., description='Total number of items across all pages')


class TimestampMixin(BaseModel):
    created_at: datetime = Field(..., description='Record creation timestamp')
    updated_at: datetime = Field(..., description='Record last update timestamp')
