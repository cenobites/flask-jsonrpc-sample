from __future__ import annotations

import uuid

from flask.testing import FlaskClient

from lms.infrastructure.database.models.patrons import PatronStatus

from .factories import BranchFactory, PatronFactory


def test_patron_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Patron.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_patron_list_with_patrons(client: FlaskClient) -> None:
    PatronFactory(name='Alice Smith', email='alice@test.com')
    PatronFactory(name='Bob Jones', email='bob@test.com')

    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Patron.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_patron_create_success(client: FlaskClient) -> None:
    branch = BranchFactory(name='Main Library')

    rv = client.post(
        '/api/patrons',
        json={
            'jsonrpc': '2.0',
            'method': 'Patron.create',
            'params': {
                'patron': {'name': 'John Smith', 'email': 'john.smith@example.com', 'branch_id': str(branch.id)}
            },
            'id': str(uuid.uuid4()),
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    patron = rv_data['result']
    assert patron['name'] == 'John Smith'
    assert patron['email'] == 'john.smith@example.com'
    assert patron['branch_id'] == str(branch.id)
    assert patron['status'] == PatronStatus.ACTIVE.value
    assert 'member_since' in patron


def test_patron_create_duplicate_email(client: FlaskClient) -> None:
    branch = BranchFactory(name='Library')
    PatronFactory(name='Existing Patron', email='duplicate@test.com', branch=branch)

    rv = client.post(
        '/api/patrons',
        json={
            'jsonrpc': '2.0',
            'method': 'Patron.create',
            'params': {'patron': {'name': 'New Patron', 'email': 'duplicate@test.com', 'branch_id': str(branch.id)}},
            'id': str(uuid.uuid4()),
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'error': {
            'code': -32000,
            'data': {'message': 'Patron with email "duplicate@test.com" already exists'},
            'message': 'Server error',
            'name': 'ServerError',
        },
    }


def test_patron_get_success(client: FlaskClient) -> None:
    patron = PatronFactory(name='Test Patron', email='test@patron.com')

    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.get',
            'params': {'patron_id': str(patron.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(patron.id)
    assert rv_data['result']['name'] == 'Test Patron'
    assert rv_data['result']['email'] == 'test@patron.com'


def test_patron_get_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/patrons',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Patron.get', 'params': {'patron_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'error': {
            'code': -32000,
            'data': {'message': f'Patron with id {fake_id} not found'},
            'message': 'Server error',
            'name': 'ServerError',
        },
    }


def test_patron_update_name_success(client: FlaskClient) -> None:
    patron = PatronFactory(name='Old Name', email='patron@test.com')

    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.update',
            'params': {'patron': {'id': str(patron.id), 'name': 'New Name'}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['name'] == 'New Name'
    assert rv_data['result']['email'] == 'patron@test.com'


def test_patron_update_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.update',
            'params': {'patron': {'id': fake_id, 'name': 'New Name'}},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_patron_update_email_success(client: FlaskClient) -> None:
    patron = PatronFactory(name='Patron', email='old@test.com')

    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.update_email',
            'params': {'patron': {'patron_id': str(patron.id), 'email': 'new@test.com'}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['email'] == 'new@test.com'
    assert rv_data['result']['name'] == 'Patron'


def test_patron_update_email_duplicate(client: FlaskClient) -> None:
    PatronFactory(name='Patron 1', email='existing@test.com')
    patron2 = PatronFactory(name='Patron 2', email='patron2@test.com')

    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.update_email',
            'params': {'patron': {'patron_id': str(patron2.id), 'email': 'existing@test.com'}},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data
    assert rv_data == {
        'jsonrpc': '2.0',
        'id': rv_data['id'],
        'error': {
            'code': -32000,
            'data': {'message': 'Patron with email "existing@test.com" already exists'},
            'message': 'Server error',
            'name': 'ServerError',
        },
    }


def test_patron_update_email_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.update_email',
            'params': {'patron': {'patron_id': fake_id, 'email': 'new@test.com'}},
        },
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_complete_patron_workflow(client: FlaskClient) -> None:
    branch = BranchFactory(name='Downtown Library')

    # Create a patron
    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.create',
            'params': {'patron': {'name': 'Jane Doe', 'email': 'jane@test.com', 'branch_id': str(branch.id)}},
        },
    )
    assert rv.status_code == 200, rv.data
    patron_id = rv.get_json()['result']['id']

    # Update patron name
    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.update',
            'params': {'patron': {'id': patron_id, 'name': 'Jane Smith'}},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['name'] == 'Jane Smith'

    # Update patron email
    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.update_email',
            'params': {'patron': {'patron_id': patron_id, 'email': 'jane.smith@test.com'}},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['email'] == 'jane.smith@test.com'

    # Get patron to verify all updates
    rv = client.post(
        '/api/patrons',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Patron.get', 'params': {'patron_id': patron_id}},
    )
    assert rv.status_code == 200, rv.data
    result = rv.get_json()['result']
    assert result['name'] == 'Jane Smith'
    assert result['email'] == 'jane.smith@test.com'
    assert result['branch_id'] == str(branch.id)


def test_patron_creation_sets_active_status(client: FlaskClient) -> None:
    branch = BranchFactory(name='Test Branch')

    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.create',
            'params': {'patron': {'name': 'Active Patron', 'email': 'active@test.com', 'branch_id': str(branch.id)}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['status'] == PatronStatus.ACTIVE.value


def test_multiple_patrons_same_branch(client: FlaskClient) -> None:
    branch = BranchFactory(name='Community Library')

    # Create first patron
    rv1 = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.create',
            'params': {'patron': {'name': 'Patron One', 'email': 'one@test.com', 'branch_id': str(branch.id)}},
        },
    )
    assert rv1.status_code == 200, rv1.data

    # Create second patron
    rv2 = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patron.create',
            'params': {'patron': {'name': 'Patron Two', 'email': 'two@test.com', 'branch_id': str(branch.id)}},
        },
    )
    assert rv2.status_code == 200, rv2.data

    # Verify both have same branch_id
    assert rv1.get_json()['result']['branch_id'] == str(branch.id)
    assert rv2.get_json()['result']['branch_id'] == str(branch.id)

    # List all patrons
    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Patron.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    assert rv.get_json()['result']['count'] == 2
