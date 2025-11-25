from __future__ import annotations

import uuid

from flask.testing import FlaskClient

from tests.unit.factories import (
    ItemFactory,
    StaffFactory,
    VendorFactory,
    AcquisitionOrderFactory,
    AcquisitionOrderLineFactory,
)
from lms.infrastructure.database.models.acquisitions import OrderStatus


def test_vendor_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/acquisitions', json={'jsonrpc': '2.0', 'method': 'Vendors.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_vendor_list_with_vendors(client: FlaskClient) -> None:
    VendorFactory(name='Vendor A')
    VendorFactory(name='Vendor B')

    rv = client.post(
        '/api/acquisitions', json={'jsonrpc': '2.0', 'method': 'Vendors.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_vendor_register_minimal(client: FlaskClient) -> None:
    staff = StaffFactory(name='Staff Member', email='staff@test.com')

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.register',
            'params': {'vendor': {'name': 'New Vendor', 'staff_id': str(staff.id)}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    vendor = rv_data['result']
    assert vendor['name'] == 'New Vendor'
    assert vendor['status'] == 'active'
    assert vendor['address'] is None
    assert vendor['email'] is None
    assert vendor['phone'] is None


def test_vendor_register_with_all_fields(client: FlaskClient) -> None:
    staff = StaffFactory(name='Staff Member', email='staff@test.com')

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.register',
            'params': {
                'vendor': {
                    'name': 'Complete Vendor',
                    'staff_id': str(staff.id),
                    'address': '123 Vendor St',
                    'email': 'vendor@test.com',
                    'phone': '555-1234',
                }
            },
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    vendor = rv_data['result']
    assert vendor['name'] == 'Complete Vendor'
    assert vendor['address'] == '123 Vendor St'
    assert vendor['email'] == 'vendor@test.com'
    assert vendor['phone'] == '555-1234'


def test_vendor_get_success(client: FlaskClient) -> None:
    vendor = VendorFactory(name='Test Vendor', email='test@vendor.com')

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.get',
            'params': {'vendor_id': str(vendor.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(vendor.id)
    assert rv_data['result']['name'] == 'Test Vendor'
    assert rv_data['result']['email'] == 'test@vendor.com'


def test_vendor_get_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/acquisitions',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Vendors.get', 'params': {'vendor_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_vendor_update_name(client: FlaskClient) -> None:
    vendor = VendorFactory(name='Old Name')

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.update',
            'params': {'vendor': {'id': str(vendor.id), 'name': 'New Name'}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['name'] == 'New Name'


def test_vendor_update_all_fields(client: FlaskClient) -> None:
    vendor = VendorFactory(name='Original Vendor')

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.update',
            'params': {
                'vendor': {
                    'id': str(vendor.id),
                    'name': 'Updated Vendor',
                    'address': '456 New St',
                    'email': 'updated@vendor.com',
                    'phone': '555-9999',
                }
            },
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['name'] == 'Updated Vendor'
    assert rv_data['result']['address'] == '456 New St'
    assert rv_data['result']['email'] == 'updated@vendor.com'
    assert rv_data['result']['phone'] == '555-9999'


def test_vendor_update_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.update',
            'params': {'vendor': {'id': fake_id, 'name': 'New Name'}},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_acquisition_order_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/acquisitions',
        json={'jsonrpc': '2.0', 'method': 'AcquisitionOrders.list', 'params': {}, 'id': str(uuid.uuid4())},
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_acquisition_order_list_with_orders(client: FlaskClient) -> None:
    AcquisitionOrderFactory()
    AcquisitionOrderFactory()

    rv = client.post(
        '/api/acquisitions',
        json={'jsonrpc': '2.0', 'method': 'AcquisitionOrders.list', 'params': {}, 'id': str(uuid.uuid4())},
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_acquisition_order_create_without_lines(client: FlaskClient) -> None:
    vendor = VendorFactory(name='Test Vendor')
    staff = StaffFactory(name='Staff', email='staff@test.com')

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.create',
            'params': {'order': {'vendor_id': str(vendor.id), 'staff_id': str(staff.id), 'order_lines': []}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    order = rv_data['result']
    assert order['vendor_id'] == str(vendor.id)
    assert order['staff_id'] == str(staff.id)
    assert order['status'] == 'pending'
    assert order['order_lines'] == []


def test_acquisition_order_create_with_lines(client: FlaskClient) -> None:
    vendor = VendorFactory(name='Test Vendor')
    staff = StaffFactory(name='Staff', email='staff@test.com')
    item = ItemFactory(title='Test Item')

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.create',
            'params': {
                'order': {
                    'vendor_id': str(vendor.id),
                    'staff_id': str(staff.id),
                    'order_lines': [{'item_id': str(item.id), 'quantity': 10, 'unit_price': 25.50}],
                }
            },
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    order = rv_data['result']
    assert order['status'] == 'pending'
    assert len(order['order_lines']) == 1
    assert order['order_lines'][0]['item_id'] == str(item.id)
    assert order['order_lines'][0]['quantity'] == 10
    assert order['order_lines'][0]['unit_price'] == '25.5'


def test_acquisition_order_get_success(client: FlaskClient) -> None:
    order = AcquisitionOrderFactory()

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.get',
            'params': {'order_id': str(order.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(order.id)


def test_acquisition_order_get_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.get',
            'params': {'order_id': fake_id},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_acquisition_order_add_line(client: FlaskClient) -> None:
    order = AcquisitionOrderFactory()
    item = ItemFactory(title='New Item')

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.add_line',
            'params': {
                'order_line': {'order_id': str(order.id), 'item_id': str(item.id), 'quantity': 5, 'unit_price': 15.75}
            },
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert len(rv_data['result']['order_lines']) == 1
    assert rv_data['result']['order_lines'][0]['item_id'] == str(item.id)


def test_acquisition_order_remove_line(client: FlaskClient) -> None:
    order = AcquisitionOrderFactory()
    line = AcquisitionOrderLineFactory(order=order)

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.remove_line',
            'params': {'order_id': str(order.id), 'order_line_id': str(line.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert len(rv_data['result']['order_lines']) == 0


def test_acquisition_order_submit(client: FlaskClient) -> None:
    order = AcquisitionOrderFactory()
    AcquisitionOrderLineFactory(order=order)

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.submit',
            'params': {'order_id': str(order.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['status'] == 'submitted'


def test_acquisition_order_submit_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.submit',
            'params': {'order_id': fake_id},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_acquisition_order_cancel(client: FlaskClient) -> None:
    order = AcquisitionOrderFactory()

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.cancel',
            'params': {'order_id': str(order.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['status'] == 'cancelled'


def test_acquisition_order_cancel_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.cancel',
            'params': {'order_id': fake_id},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_acquisition_order_receive_line_full(client: FlaskClient) -> None:
    order = AcquisitionOrderFactory(status=OrderStatus.SUBMITTED)
    line = AcquisitionOrderLineFactory(order=order, quantity=10)

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.receive_line',
            'params': {'order_id': str(order.id), 'order_line_id': str(line.id), 'received_quantity': 10},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    order_line = rv_data['result']['order_lines'][0]
    assert order_line['received_quantity'] == 10
    assert order_line['status'] == 'received'


def test_acquisition_order_receive_line_partial(client: FlaskClient) -> None:
    order = AcquisitionOrderFactory(status=OrderStatus.SUBMITTED)
    line = AcquisitionOrderLineFactory(order=order, quantity=10)

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.receive_line',
            'params': {'order_id': str(order.id), 'order_line_id': str(line.id), 'received_quantity': 5},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    order_line = rv_data['result']['order_lines'][0]
    assert order_line['received_quantity'] == 5
    assert order_line['status'] == 'partially_received'


def test_acquisition_order_receive_line_default_quantity(client: FlaskClient) -> None:
    order = AcquisitionOrderFactory(status=OrderStatus.SUBMITTED)
    line = AcquisitionOrderLineFactory(order=order, quantity=8)

    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.receive_line',
            'params': {'order_id': str(order.id), 'order_line_id': str(line.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    order_line = rv_data['result']['order_lines'][0]
    assert order_line['received_quantity'] == 8
    assert order_line['status'] == 'received'


def test_order_with_multiple_lines(client: FlaskClient) -> None:
    vendor = VendorFactory(name='Multi Vendor')
    staff = StaffFactory(name='Staff', email='staff@test.com')
    item1 = ItemFactory(title='Item 1')
    item2 = ItemFactory(title='Item 2')
    item3 = ItemFactory(title='Item 3')

    # Create order with multiple lines
    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.create',
            'params': {
                'order': {
                    'vendor_id': str(vendor.id),
                    'staff_id': str(staff.id),
                    'order_lines': [
                        {'item_id': str(item1.id), 'quantity': 5, 'unit_price': 10.00},
                        {'item_id': str(item2.id), 'quantity': 3, 'unit_price': 15.00},
                        {'item_id': str(item3.id), 'quantity': 7, 'unit_price': 8.50},
                    ],
                }
            },
        },
    )
    assert rv.status_code == 200, rv.data
    result = rv.get_json()['result']
    assert len(result['order_lines']) == 3
