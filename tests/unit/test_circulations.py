from __future__ import annotations

import uuid

from flask.testing import FlaskClient

from lms.infrastructure.database.models.patrons import PatronStatus
from lms.infrastructure.database.models.catalogs import CopyStatus, ItemFormat
from lms.infrastructure.database.models.organization import StaffRole, BranchStatus

from .factories import (
    CopyFactory,
    ItemFactory,
    StaffFactory,
    AuthorFactory,
    BranchFactory,
    PatronFactory,
    CategoryFactory,
    PublisherFactory,
)


def test_active_circulation_flow(client: FlaskClient) -> None:
    manager = StaffFactory(role=StaffRole.MANAGER)
    branch = BranchFactory(name='Central Library', manager_id=manager.id, status=BranchStatus.ACTIVE)
    manager.managed_branch = branch
    staff = StaffFactory(branch=branch, role=StaffRole.LIBRARIAN)

    publisher = PublisherFactory()
    author = AuthorFactory(name='Jane Doe')
    category = CategoryFactory()
    item = ItemFactory(format=ItemFormat.BOOK, category=category, publisher=publisher, authors=[author])

    copies = CopyFactory.create_batch(3, item=item, branch_id=branch.id, status=CopyStatus.AVAILABLE)
    patron = PatronFactory(branch=branch, status=PatronStatus.ACTIVE)

    # Borrow a copy
    rv = client.post(
        '/api/circulation',
        json={
            'jsonrpc': '2.0',
            'method': 'Loan.checkout_copy',
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
        '/api/catalog',
        json={'jsonrpc': '2.0', 'method': 'Copy.get', 'params': {'copy_id': copies[0].id}, 'id': str(uuid.uuid4())},
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
        '/api/circulation',
        json={
            'jsonrpc': '2.0',
            'method': 'Loan.checkin_copy',
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
        '/api/catalog',
        json={'jsonrpc': '2.0', 'method': 'Copy.get', 'params': {'copy_id': copies[0].id}, 'id': str(uuid.uuid4())},
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
