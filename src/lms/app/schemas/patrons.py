from __future__ import annotations

from pydantic import Field, EmailStr

from . import BaseSchema


class PatronCreate(BaseSchema):
    branch_id: str = Field(description='Branch ID')
    name: str = Field(min_length=1, max_length=300, description='Patron name')
    email: EmailStr = Field(description='Patron email address')


class PatronUpdate(BaseSchema):
    id: str = Field(description='Patron ID')
    name: str = Field(min_length=1, max_length=300, description='Patron name')
