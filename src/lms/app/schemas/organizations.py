from __future__ import annotations

from pydantic import Field, EmailStr

from . import BaseSchema


class BranchCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=100, description='Branch name')
    manager_id: str | None = Field(None, description='ID of the branch manager')
    address: str | None = Field(None, max_length=255, description='Branch address')
    phone: str | None = Field(None, max_length=20, description='Branch phone number')
    email: str | None = Field(None, max_length=100, description='Branch email address')
    manager_id: str | None = Field(None, description='Manager ID')


class BranchUpdate(BaseSchema):
    branch_id: str = Field(description='Branch ID')
    name: str = Field(min_length=1, max_length=100, description='Branch name')
    address: str | None = Field(None, max_length=255, description='Branch address')
    phone: str | None = Field(None, max_length=20, description='Branch phone number')


class StaffCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=100, description='Staff name')
    email: EmailStr = Field(description='Staff email address')
    role: str = Field(description='Staff role (librarian, technician, manager)')


class StaffUpdate(BaseSchema):
    staff_id: str = Field(description='Unique staff identifier')
    name: str = Field(min_length=1, max_length=100, description='Staff name')
