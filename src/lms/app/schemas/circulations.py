from __future__ import annotations

from datetime import datetime

from pydantic import Field

from . import BaseSchema


class LoanUpdate(BaseSchema):
    id: str = Field(description='ID of the loan to update')


class HoldSchema(BaseSchema):
    patron_id: str = Field(..., description='ID of the patron placing the hold')
    item_id: str = Field(..., description='ID of the item being held')
    expiry_date: datetime = Field(..., description='Date when hold expires')


class HoldCreate(HoldSchema):
    pass


class HoldUpdate(HoldSchema):
    id: str = Field(..., description='ID of the hold to update')
