from __future__ import annotations

import uuid

from flask.testing import FlaskClient

from lms.infrastructure.database.models.organization import StaffRole

from .factories import StaffFactory, BranchFactory


def test_branch_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/organization', json={'jsonrpc': '2.0', 'method': 'Branch.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_branch_list_with_branches(client: FlaskClient) -> None:
    BranchFactory(name='Main Library')
    BranchFactory(name='Downtown Branch')

    rv = client.post(
        '/api/organization', json={'jsonrpc': '2.0', 'method': 'Branch.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_branch_create_minimal(client: FlaskClient) -> None:
    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.create',
            'params': {'branch': {'name': 'New Branch'}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    branch = rv_data['result']
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'result': {
            'id': branch['id'],
            'manager_id': None,
            'name': 'New Branch',
            'status': 'open',
            'address': None,
            'email': None,
            'phone': None,
        },
    }


def test_branch_create_with_all_fields(client: FlaskClient) -> None:
    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.create',
            'params': {
                'branch': {
                    'name': 'Complete Branch',
                    'address': '123 Main Street',
                    'phone': '555-1234',
                    'email': 'complete@library.com',
                }
            },
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    branch = rv_data['result']
    assert branch['name'] == 'Complete Branch'
    assert branch['address'] == '123 Main Street'
    assert branch['phone'] == '555-1234'
    assert branch['email'] == 'complete@library.com'


def test_branch_create_duplicate_name(client: FlaskClient) -> None:
    BranchFactory(name='Central Library')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.create',
            'params': {'branch': {'name': 'Central Library'}},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'error': {
            'code': -32000,
            'data': {'code': 'DuplicateBranchNameError', 'detail': 'Branch with name "Central Library" already exists'},
            'message': 'Server error',
            'name': 'ServerError',
        },
    }


def test_branch_get_success(client: FlaskClient) -> None:
    branch = BranchFactory(name='Test Branch', address='456 Oak Ave')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.get',
            'params': {'branch_id': str(branch.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(branch.id)
    assert rv_data['result']['name'] == 'Test Branch'
    assert rv_data['result']['address'] == '456 Oak Ave'


def test_branch_get_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Branch.get', 'params': {'branch_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data
    assert rv_data['error']['data']['code'] == 'BranchDoesNotExistError'


def test_branch_update_name(client: FlaskClient) -> None:
    branch = BranchFactory(name='Old Name')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.update',
            'params': {'branch': {'branch_id': str(branch.id), 'name': 'New Name'}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['name'] == 'New Name'


def test_branch_update_all_fields(client: FlaskClient) -> None:
    branch = BranchFactory(name='Original Branch')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.update',
            'params': {
                'branch': {
                    'branch_id': str(branch.id),
                    'name': 'Updated Branch',
                    'address': '789 Elm St',
                    'phone': '555-9999',
                }
            },
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['name'] == 'Updated Branch'
    assert rv_data['result']['address'] == '789 Elm St'
    assert rv_data['result']['phone'] == '555-9999'


def test_branch_update_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.update',
            'params': {'branch': {'branch_id': fake_id, 'name': 'New Name'}},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_branch_assign_manager_success(client: FlaskClient) -> None:
    branch = BranchFactory(name='Test Branch')
    staff = StaffFactory(name='Manager One', email='manager@test.com', role=StaffRole.MANAGER)

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.assign_manager',
            'params': {'branch_id': str(branch.id), 'manager_id': str(staff.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['manager_id'] == str(staff.id)
    assert rv_data['result']['status'] == 'active'


def test_branch_assign_manager_branch_not_found(client: FlaskClient) -> None:
    staff = StaffFactory(name='Manager', email='mgr@test.com')
    fake_branch_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.assign_manager',
            'params': {'branch_id': fake_branch_id, 'manager_id': str(staff.id)},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_branch_assign_manager_staff_not_found(client: FlaskClient) -> None:
    branch = BranchFactory(name='Test Branch')
    fake_staff_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.assign_manager',
            'params': {'branch_id': str(branch.id), 'manager_id': fake_staff_id},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_branch_close_success(client: FlaskClient) -> None:
    branch = BranchFactory(name='To Close Branch')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.close',
            'params': {'branch_id': str(branch.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result'] is None


def test_branch_close_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Branch.close', 'params': {'branch_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_staff_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/organization', json={'jsonrpc': '2.0', 'method': 'Staff.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_staff_list_with_staff(client: FlaskClient) -> None:
    StaffFactory(name='Alice', email='alice@test.com')
    StaffFactory(name='Bob', email='bob@test.com')

    rv = client.post(
        '/api/organization', json={'jsonrpc': '2.0', 'method': 'Staff.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_staff_create_success(client: FlaskClient) -> None:
    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.create',
            'params': {'staff': {'name': 'Jane Doe', 'email': 'jane@test.com', 'role': 'librarian'}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    staff = rv_data['result']
    assert staff['name'] == 'Jane Doe'
    assert staff['email'] == 'jane@test.com'
    assert staff['role'] == 'librarian'
    assert staff['branch_id'] is None


def test_staff_create_duplicate_email(client: FlaskClient) -> None:
    StaffFactory(name='Existing Staff', email='duplicate@test.com')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.create',
            'params': {'staff': {'name': 'New Staff', 'email': 'duplicate@test.com', 'role': 'librarian'}},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data
    assert rv_data['error']['data']['code'] == 'DuplicateStaffEmailError'


def test_staff_get_success(client: FlaskClient) -> None:
    staff = StaffFactory(name='Test Staff', email='test@staff.com')

    rv = client.post(
        '/api/organization',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Staff.get', 'params': {'staff_id': str(staff.id)}},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(staff.id)
    assert rv_data['result']['name'] == 'Test Staff'
    assert rv_data['result']['email'] == 'test@staff.com'


def test_staff_get_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Staff.get', 'params': {'staff_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data
    assert rv_data['error']['data']['code'] == 'StaffDoesNotExistError'


def test_staff_update_name(client: FlaskClient) -> None:
    staff = StaffFactory(name='Old Name', email='staff@test.com')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.update',
            'params': {'staff': {'staff_id': str(staff.id), 'name': 'New Name'}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['name'] == 'New Name'
    assert rv_data['result']['email'] == 'staff@test.com'


def test_staff_update_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.update',
            'params': {'staff': {'staff_id': fake_id, 'name': 'New Name'}},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_staff_update_email_success(client: FlaskClient) -> None:
    staff = StaffFactory(name='Staff Member', email='old@test.com')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.update_email',
            'params': {'staff_id': str(staff.id), 'email': 'new@test.com'},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['email'] == 'new@test.com'


def test_staff_update_email_duplicate(client: FlaskClient) -> None:
    StaffFactory(name='Staff 1', email='existing@test.com')
    staff2 = StaffFactory(name='Staff 2', email='staff2@test.com')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.update_email',
            'params': {'staff_id': str(staff2.id), 'email': 'existing@test.com'},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_staff_update_email_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.update_email',
            'params': {'staff_id': fake_id, 'email': 'new@test.com'},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_staff_update_role_success(client: FlaskClient) -> None:
    staff = StaffFactory(name='Staff', email='staff@test.com', role=StaffRole.LIBRARIAN)

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.update_role',
            'params': {'staff_id': str(staff.id), 'role': 'manager'},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['role'] == 'manager'


def test_staff_update_role_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.update_role',
            'params': {'staff_id': fake_id, 'role': 'manager'},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_staff_inactivate_success(client: FlaskClient) -> None:
    staff = StaffFactory(name='Active Staff', email='active@test.com')

    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Staff.inactivate',
            'params': {'staff_id': str(staff.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    # Verify the staff was returned (implementation may vary on what gets returned)
    assert 'result' in rv_data


def test_staff_inactivate_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/organization',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Staff.inactivate', 'params': {'staff_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_complete_branch_staff_workflow(client: FlaskClient) -> None:
    # Create a branch
    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.create',
            'params': {'branch': {'name': 'Workflow Branch', 'address': '100 Test St'}},
        },
    )
    assert rv.status_code == 200, rv.data
    branch_id = rv.get_json()['result']['id']

    # Create a staff manager
    rv = client.post(
        '/api/organization',
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
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.assign_manager',
            'params': {'branch_id': branch_id, 'manager_id': manager_id},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['manager_id'] == manager_id

    # Verify staff was assigned to branch
    rv = client.post(
        '/api/organization',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Staff.get', 'params': {'staff_id': manager_id}},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['branch_id'] == branch_id

    # Update branch details
    rv = client.post(
        '/api/organization',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Branch.update',
            'params': {'branch': {'branch_id': branch_id, 'name': 'Updated Workflow Branch', 'phone': '555-7777'}},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['name'] == 'Updated Workflow Branch'

    # Update staff role
    rv = client.post(
        '/api/organization',
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
        '/api/organization',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Branch.close', 'params': {'branch_id': branch_id}},
    )
    assert rv.status_code == 200, rv.data
