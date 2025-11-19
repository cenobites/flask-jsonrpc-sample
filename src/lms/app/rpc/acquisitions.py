from __future__ import annotations

import typing as t

from flask import current_app

from flask_jsonrpc import JSONRPCBlueprint
import flask_jsonrpc.types.params as tp
import flask_jsonrpc.types.methods as tm

from lms.app.schemas import Page
from lms.app.schemas.acquisitions import OrderCreate, OrderLineAdd, VendorUpdate, VendorRegister
from lms.app.services.acquisitions import VendorService, AcquisitionOrderService
from lms.domain.acquisitions.entities import Vendor, AcquisitionOrder

jsonrpc_bp = JSONRPCBlueprint('acquisitions', __name__)


@jsonrpc_bp.method(
    'AcquisitionOrders.list',
    tm.MethodAnnotated[
        tm.Summary('List acquisition orders'),
        tm.Description('Get a list of all acquisition orders'),
        tm.Tag(name='acquisitions', summary='Acquisitions Management', description='Library acquisition operations'),
    ],
)
def list_orders() -> t.Annotated[Page[AcquisitionOrder], tp.Summary('List of orders')]:
    acquisition_order_service: AcquisitionOrderService = current_app.container.acquisition_order_service()  # type: ignore
    orders = acquisition_order_service.find_all_orders()
    return Page[AcquisitionOrder](results=orders, count=len(orders))


@jsonrpc_bp.method(
    'AcquisitionOrders.get',
    tm.MethodAnnotated[
        tm.Summary('Get order by ID'),
        tm.Description('Retrieve details of a specific acquisition order'),
        tm.Tag(name='acquisitions'),
    ],
)
def get_order(
    order_id: t.Annotated[str, tp.Summary('Order ID'), tp.Required()],
) -> t.Annotated[AcquisitionOrder, tp.Summary('Order information')]:
    acquisition_order_service: AcquisitionOrderService = current_app.container.acquisition_order_service()  # type: ignore
    return acquisition_order_service.get_order(order_id)


@jsonrpc_bp.method(
    'AcquisitionOrders.create',
    tm.MethodAnnotated[
        tm.Summary('Create acquisition order'),
        tm.Description('Create a new acquisition order'),
        tm.Tag(name='acquisitions'),
    ],
)
def create_order(
    order: t.Annotated[OrderCreate, tp.Summary('Order information'), tp.Required()],
) -> t.Annotated[AcquisitionOrder, tp.Summary('Created order information')]:
    acquisition_order_service: AcquisitionOrderService = current_app.container.acquisition_order_service()  # type: ignore
    acquisition_order = acquisition_order_service.create_order(vendor_id=order.vendor_id, staff_id=order.staff_id)
    for line in order.order_lines:
        acquisition_order = acquisition_order_service.add_line_to_order(
            order_id=t.cast(str, acquisition_order.id),
            item_id=line.item_id,
            quantity=line.quantity,
            unit_price=line.unit_price,
        )
    return acquisition_order


@jsonrpc_bp.method(
    'AcquisitionOrders.add_line',
    tm.MethodAnnotated[
        tm.Summary('Update acquisition order'),
        tm.Description('Partially update fields of an acquisition order such as status or received_date'),
        tm.Tag(name='acquisitions'),
        tm.Error(code=-32001, message='Order update failed', data={'reason': 'order not found or invalid data'}),
        tm.Example(
            name='update_order_example',
            summary='Update existing order status',
            params=[
                tm.ExampleField(name='order_id', value=1, summary='Order ID'),
                tm.ExampleField(name='status', value='received', summary='New status'),
            ],
        ),
    ],
)
def add_order_line(
    order_line: t.Annotated[OrderLineAdd, tp.Summary('Order line information')],
) -> t.Annotated[AcquisitionOrder, tp.Summary('Updated order information')]:
    acquisition_order_service: AcquisitionOrderService = current_app.container.acquisition_order_service()  # type: ignore
    return acquisition_order_service.add_line_to_order(
        order_id=order_line.order_id,
        item_id=order_line.item_id,
        quantity=order_line.quantity,
        unit_price=order_line.unit_price,
    )


@jsonrpc_bp.method(
    'AcquisitionOrders.remove_line',
    tm.MethodAnnotated[
        tm.Summary('Update acquisition order'),
        tm.Description('Partially update fields of an acquisition order such as status or received_date'),
        tm.Tag(name='acquisitions'),
        tm.Error(code=-32001, message='Order update failed', data={'reason': 'order not found or invalid data'}),
        tm.Example(
            name='update_order_example',
            summary='Update existing order status',
            params=[
                tm.ExampleField(name='order_id', value=1, summary='Order ID'),
                tm.ExampleField(name='status', value='received', summary='New status'),
            ],
        ),
    ],
)
def remove_order_line(
    order_id: t.Annotated[str, tp.Summary('Order ID'), tp.Required()],
    order_line_id: t.Annotated[str, tp.Summary('Order Line ID'), tp.Required()],
) -> t.Annotated[AcquisitionOrder, tp.Summary('Updated order information')]:
    acquisition_order_service: AcquisitionOrderService = current_app.container.acquisition_order_service()  # type: ignore
    return acquisition_order_service.remove_line_from_order(order_id=order_id, order_line_id=order_line_id)


@jsonrpc_bp.method(
    'AcquisitionOrders.receive_line',
    tm.MethodAnnotated[
        tm.Summary('Update acquisition order'),
        tm.Description('Partially update fields of an acquisition order such as status or received_date'),
        tm.Tag(name='acquisitions'),
        tm.Error(code=-32001, message='Order update failed', data={'reason': 'order not found or invalid data'}),
        tm.Example(
            name='update_order_example',
            summary='Update existing order status',
            params=[
                tm.ExampleField(name='order_id', value=1, summary='Order ID'),
                tm.ExampleField(name='status', value='received', summary='New status'),
            ],
        ),
    ],
)
def receive_order_line(
    order_id: t.Annotated[str, tp.Summary('Order ID'), tp.Required()],
    order_line_id: t.Annotated[str, tp.Summary('Order Line ID'), tp.Required()],
    received_quantity: t.Annotated[int | None, tp.Summary('Received Quantity')] = None,
) -> t.Annotated[AcquisitionOrder, tp.Summary('Updated order information')]:
    acquisition_order_service: AcquisitionOrderService = current_app.container.acquisition_order_service()  # type: ignore
    return acquisition_order_service.receive_line_from_order(
        order_id=order_id, order_line_id=order_line_id, received_quantity=received_quantity
    )


@jsonrpc_bp.method(
    'AcquisitionOrders.submit',
    tm.MethodAnnotated[
        tm.Summary('Submit order'), tm.Description('Submit an acquisition order'), tm.Tag(name='acquisitions')
    ],
)
def submit_order(
    order_id: t.Annotated[str, tp.Summary('Order ID'), tp.Required()],
) -> t.Annotated[AcquisitionOrder, tp.Summary('Submitted order information')]:
    acquisition_order_service: AcquisitionOrderService = current_app.container.acquisition_order_service()  # type: ignore
    return acquisition_order_service.submit_order(order_id)


@jsonrpc_bp.method(
    'AcquisitionOrders.cancel',
    tm.MethodAnnotated[
        tm.Summary('Cancel order'), tm.Description('Cancel an acquisition order'), tm.Tag(name='acquisitions')
    ],
)
def cancel_order(
    order_id: t.Annotated[str, tp.Summary('Order ID'), tp.Required()],
) -> t.Annotated[AcquisitionOrder, tp.Summary('Cancelled order information')]:
    acquisition_order_service: AcquisitionOrderService = current_app.container.acquisition_order_service()  # type: ignore
    return acquisition_order_service.cancel_order(order_id)


@jsonrpc_bp.method(
    'Vendors.list',
    tm.MethodAnnotated[
        tm.Summary('Get all vendors'),
        tm.Description('Retrieve a list of all vendors'),
        tm.Tag(name='acquisitions'),
        tm.Error(code=-32002, message='No vendors found', data={'reason': 'no vendors available'}),
        tm.Example(name='all_vendors_example', params=[]),
    ],
)
def list_vendors() -> t.Annotated[Page[Vendor], tp.Summary('Vendor search result')]:
    vendor_service: VendorService = current_app.container.vendor_service()  # type: ignore
    vendors = vendor_service.find_all_vendors()
    return Page[Vendor](results=vendors, count=len(vendors))


@jsonrpc_bp.method(
    'Vendors.get',
    tm.MethodAnnotated[
        tm.Summary('Get vendor by ID'),
        tm.Description('Retrieve vendor information using its unique ID'),
        tm.Tag(name='acquisitions'),
        tm.Error(code=-32002, message='Vendor not found', data={'reason': 'invalid vendor ID'}),
        tm.Example(name='get_vendor_example', params=[tm.ExampleField(name='vendor_id', value=1, summary='Vendor ID')]),
    ],
)
def get_vendor(
    vendor_id: t.Annotated[str, tp.Summary('Vendor ID'), tp.Required()],
) -> t.Annotated[Vendor, tp.Summary('Vendor information')]:
    vendor_service: VendorService = current_app.container.vendor_service()  # type: ignore
    return vendor_service.get_vendor(vendor_id)


@jsonrpc_bp.method(
    'Vendors.register',
    tm.MethodAnnotated[
        tm.Summary('Create vendor'),
        tm.Description('Create a new vendor'),
        tm.Tag(name='acquisitions'),
        tm.Error(code=-32001, message='Vendor creation failed', data={'reason': 'duplicate name or invalid data'}),
        tm.Example(
            name='create_vendor_example',
            summary='Create new vendor',
            params=[
                tm.ExampleField(
                    name='vendor_data',
                    value={'name': 'Acme Books', 'address': '42 Paper Rd', 'phone': '555-0200'},
                    summary='Vendor data object',
                )
            ],
        ),
    ],
)
def register_vendor(
    vendor: t.Annotated[VendorRegister, tp.Summary('Vendor information'), tp.Required()],
) -> t.Annotated[Vendor, tp.Summary('Created vendor information')]:
    vendor_service: VendorService = current_app.container.vendor_service()  # type: ignore
    return vendor_service.register_vendor(
        name=vendor.name, staff_id=vendor.staff_id, address=vendor.address, email=vendor.email, phone=vendor.phone
    )


@jsonrpc_bp.method(
    'Vendors.update',
    tm.MethodAnnotated[
        tm.Summary('Update vendor'),
        tm.Description('Update an existing vendor'),
        tm.Tag(name='acquisitions'),
        tm.Error(code=-32001, message='Vendor update failed', data={'reason': 'vendor not found or invalid data'}),
        tm.Example(
            name='update_vendor_example',
            summary='Update existing vendor',
            params=[
                tm.ExampleField(name='vendor_id', value=1, summary='Vendor ID'),
                tm.ExampleField(
                    name='vendor_data',
                    value={'name': 'Acme Books Updated', 'phone': '555-0300'},
                    summary='Vendor data object',
                ),
            ],
        ),
    ],
)
def update_vendor(
    vendor: t.Annotated[VendorUpdate, tp.Summary('Vendor update data'), tp.Required()],
) -> t.Annotated[Vendor, tp.Summary('Updated vendor information')]:
    vendor_service: VendorService = current_app.container.vendor_service()  # type: ignore
    return vendor_service.update_vendor(
        vendor.id, name=vendor.name, address=vendor.address, email=vendor.email, phone=vendor.phone
    )
