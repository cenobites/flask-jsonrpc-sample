from __future__ import annotations

import uuid

from flask.testing import FlaskClient

from tests.unit.factories import (
    CopyFactory,
    ItemFactory,
    StaffFactory,
    AuthorFactory,
    BranchFactory,
    PatronFactory,
    CategoryFactory,
    PublisherFactory,
)
from lms.infrastructure.database.models.patrons import PatronStatus
from lms.infrastructure.database.models.catalogs import CopyStatus, ItemFormat
from lms.infrastructure.database.models.organizations import StaffRole, BranchStatus


def test_complete_acquisition_workflow(client: FlaskClient) -> None:
    staff = StaffFactory(name='Librarian', email='librarian@test.com')

    # Register vendor
    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.register',
            'params': {'vendor': {'name': 'Book Supplier', 'staff_id': str(staff.id), 'email': 'supplier@test.com'}},
        },
    )
    assert rv.status_code == 200, rv.data
    vendor_id = rv.get_json()['result']['id']

    # Create order without lines
    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.create',
            'params': {'order': {'vendor_id': vendor_id, 'staff_id': str(staff.id), 'order_lines': []}},
        },
    )
    assert rv.status_code == 200, rv.data
    order_id = rv.get_json()['result']['id']

    # Add line to order
    item = ItemFactory(title='Book Title')
    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.add_line',
            'params': {
                'order_line': {'order_id': order_id, 'item_id': str(item.id), 'quantity': 20, 'unit_price': 12.99}
            },
        },
    )
    assert rv.status_code == 200, rv.data
    line_id = rv.get_json()['result']['order_lines'][0]['id']

    # Submit order
    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.submit',
            'params': {'order_id': order_id},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == 'submitted'

    # Receive line
    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'AcquisitionOrders.receive_line',
            'params': {'order_id': order_id, 'order_line_id': line_id, 'received_quantity': 20},
        },
    )
    assert rv.status_code == 200, rv.data
    result = rv.get_json()['result']
    assert result['status'] == 'received'
    assert result['order_lines'][0]['status'] == 'received'


def test_vendor_update_workflow(client: FlaskClient) -> None:
    staff = StaffFactory(name='Staff', email='staff@test.com')

    # Register vendor
    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.register',
            'params': {'vendor': {'name': 'Initial Name', 'staff_id': str(staff.id)}},
        },
    )
    assert rv.status_code == 200, rv.data
    vendor_id = rv.get_json()['result']['id']

    # Update vendor
    rv = client.post(
        '/api/acquisitions',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Vendors.update',
            'params': {
                'vendor': {
                    'id': vendor_id,
                    'name': 'Updated Name',
                    'email': 'updated@vendor.com',
                    'phone': '555-7777',
                    'address': '789 Vendor Rd',
                }
            },
        },
    )
    assert rv.status_code == 200, rv.data

    # Get vendor to verify updates
    rv = client.post(
        '/api/acquisitions',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Vendors.get', 'params': {'vendor_id': vendor_id}},
    )
    assert rv.status_code == 200, rv.data
    result = rv.get_json()['result']
    assert result['name'] == 'Updated Name'
    assert result['email'] == 'updated@vendor.com'
    assert result['phone'] == '555-7777'
    assert result['address'] == '789 Vendor Rd'


def test_complete_branch_staff_workflow(client: FlaskClient) -> None:
    # Create a branch
    rv = client.post(
        '/api/organizations',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branches.create',
            'params': {'branch': {'name': 'Workflow Branch', 'address': '100 Test St'}},
        },
    )
    assert rv.status_code == 200, rv.data
    branch_id = rv.get_json()['result']['id']

    # Create a staff manager
    rv = client.post(
        '/api/organizations',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.create',
            'params': {'staff': {'name': 'Manager Smith', 'email': 'smith@test.com', 'role': 'manager'}},
        },
    )
    assert rv.status_code == 200, rv.data
    manager_id = rv.get_json()['result']['id']

    # Assign manager to branch
    rv = client.post(
        '/api/organizations',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branches.assign_manager',
            'params': {'branch_id': branch_id, 'manager_id': manager_id},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['manager_id'] == manager_id

    # Verify staff was assigned to branch
    rv = client.post(
        '/api/organizations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Staff.get', 'params': {'staff_id': manager_id}},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['branch_id'] == branch_id

    # Update branch details
    rv = client.post(
        '/api/organizations',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branches.update',
            'params': {'branch': {'branch_id': branch_id, 'name': 'Updated Workflow Branch', 'phone': '555-7777'}},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['name'] == 'Updated Workflow Branch'

    # Update staff role
    rv = client.post(
        '/api/organizations',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.update_role',
            'params': {'staff_id': manager_id, 'role': 'technician'},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['role'] == 'technician'

    # Close branch
    rv = client.post(
        '/api/organizations',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branches.close',
            'params': {'branch_id': branch_id},
        },
    )
    assert rv.status_code == 200, rv.data


def test_active_circulation_flow(client: FlaskClient) -> None:
    manager = StaffFactory(role=StaffRole.MANAGER)
    branch = BranchFactory(name='Central Library', manager_id=manager.id, status=BranchStatus.ACTIVE)
    manager.managed_branch = branch
    staff = StaffFactory(branch=branch, role=StaffRole.LIBRARIAN)

    publisher = PublisherFactory()
    author = AuthorFactory(name='Jane Doe')
    category = CategoryFactory()
    item = ItemFactory(format=ItemFormat.BOOK, category=category, publisher=publisher, authors=[author])

    copies = CopyFactory.create_batch(3, item=item, branch=branch, status=CopyStatus.AVAILABLE)
    patron = PatronFactory(branch=branch, status=PatronStatus.ACTIVE)

    # Borrow a copy
    rv = client.post(
        '/api/circulations',
        json={
            'jsonrpc': '2.0',
            'method': 'Loans.checkout_copy',
            'params': {'patron_id': patron.id, 'copy_id': copies[0].id, 'staff_id': staff.id},
            'id': str(uuid.uuid4()),
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    loan = rv_data['result']
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'result': {
            'id': loan['id'],
            'branch_id': str(branch.id),
            'patron_id': str(patron.id),
            'copy_id': str(copies[0].id),
            'staff_out_id': str(staff.id),
            'staff_in_id': None,
            'loan_date': loan['loan_date'],
            'due_date': loan['due_date'],
            'return_date': None,
        },
    }

    # Check that the copy status is now CHECKED_OUT
    rv = client.post(
        '/api/catalogs',
        json={'jsonrpc': '2.0', 'method': 'Copies.get', 'params': {'copy_id': copies[0].id}, 'id': str(uuid.uuid4())},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    copy = rv_data['result']
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'result': {
            'id': copy['id'],
            'item_id': str(item.id),
            'branch_id': str(branch.id),
            'barcode': copy['barcode'],
            'status': CopyStatus.CHECKED_OUT.value,
            'location': copy['location'],
            'acquisition_date': copy['acquisition_date'],
        },
    }

    # Return the copy
    rv = client.post(
        '/api/circulations',
        json={
            'jsonrpc': '2.0',
            'method': 'Loans.checkin_copy',
            'params': {'loan_id': loan['id'], 'staff_id': staff.id},
            'id': str(uuid.uuid4()),
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    returned_loan = rv_data['result']
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'result': {
            'id': returned_loan['id'],
            'branch_id': str(branch.id),
            'patron_id': str(patron.id),
            'copy_id': str(copies[0].id),
            'staff_out_id': str(staff.id),
            'staff_in_id': str(staff.id),
            'loan_date': loan['loan_date'],
            'due_date': loan['due_date'],
            'return_date': returned_loan['return_date'],
        },
    }

    # Check that the copy status is now AVAILABLE
    rv = client.post(
        '/api/catalogs',
        json={'jsonrpc': '2.0', 'method': 'Copies.get', 'params': {'copy_id': copies[0].id}, 'id': str(uuid.uuid4())},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    copy = rv_data['result']
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'result': {
            'id': copy['id'],
            'item_id': str(item.id),
            'branch_id': str(branch.id),
            'barcode': copy['barcode'],
            'status': CopyStatus.AVAILABLE.value,
            'location': copy['location'],
            'acquisition_date': copy['acquisition_date'],
        },
    }
