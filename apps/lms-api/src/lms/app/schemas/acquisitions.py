from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from . import BaseSchema


class OrderLineCreate(BaseSchema):
    item_id: str = Field(description='ID of the item to be acquired')
    quantity: int = Field(description='Quantity of the item to be acquired')
    unit_price: Decimal = Field(description='Unit price of the item to be acquired')


class OrderCreate(BaseSchema):
    vendor_id: str = Field(description='ID of the vendor')
    staff_id: str = Field(description='ID of the staff creating the order')
    order_lines: list[OrderLineCreate] = Field(description='List of order lines', default_factory=list)


class OrderLineAdd(BaseSchema):
    order_id: str = Field(description='ID of the acquisition order')
    item_id: str = Field(description='ID of the item to be acquired')
    quantity: int = Field(description='Quantity of the item to be acquired')
    unit_price: Decimal = Field(description='Unit price of the item to be acquired')


class VendorRegister(BaseSchema):
    name: str = Field(max_length=255, description='Vendor name address')
    staff_id: str = Field(description='ID of the staff registering the vendor')
    email: str | None = Field(None, max_length=255, description='Vendor email address')
    phone: str | None = Field(None, max_length=20, description='Vendor phone number')
    address: str | None = Field(None, description='Vendor address')


class VendorUpdate(BaseSchema):
    id: str = Field(description='Vendor ID')
    name: str = Field(max_length=255, description='Vendor name address')
    email: str | None = Field(None, max_length=255, description='Vendor email address')
    phone: str | None = Field(None, max_length=20, description='Vendor phone number')
    address: str | None = Field(None, description='Vendor address')
