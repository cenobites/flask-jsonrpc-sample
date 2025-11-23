from __future__ import annotations

import uuid
from decimal import Decimal

from flask.testing import FlaskClient

from lms.infrastructure.database.models.patrons import FineStatus, PatronStatus

from ...factories import FineFactory, BranchFactory, PatronFactory


def test_patron_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Patrons.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_patron_list_with_patrons(client: FlaskClient) -> None:
    PatronFactory(name='Alice Smith', email='alice@test.com')
    PatronFactory(name='Bob Jones', email='bob@test.com')

    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Patrons.list', 'params': {}, 'id': str(uuid.uuid4())}
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
            'method': 'Patrons.create',
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
            'method': 'Patrons.create',
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
            'method': 'Patrons.get',
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
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Patrons.get', 'params': {'patron_id': fake_id}},
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
            'method': 'Patrons.update',
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
            'method': 'Patrons.update',
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
            'method': 'Patrons.update_email',
            'params': {'patron_id': str(patron.id), 'email': 'new@test.com'},
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
            'method': 'Patrons.update_email',
            'params': {'patron_id': str(patron2.id), 'email': 'existing@test.com'},
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
            'method': 'Patrons.update_email',
            'params': {'patron_id': fake_id, 'email': 'new@test.com'},
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
            'method': 'Patrons.create',
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
            'method': 'Patrons.update',
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
            'method': 'Patrons.update_email',
            'params': {'patron_id': patron_id, 'email': 'jane.smith@test.com'},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['email'] == 'jane.smith@test.com'

    # Get patron to verify all updates
    rv = client.post(
        '/api/patrons',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Patrons.get', 'params': {'patron_id': patron_id}},
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
            'method': 'Patrons.create',
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
            'method': 'Patrons.create',
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
            'method': 'Patrons.create',
            'params': {'patron': {'name': 'Patron Two', 'email': 'two@test.com', 'branch_id': str(branch.id)}},
        },
    )
    assert rv2.status_code == 200, rv2.data

    # Verify both have same branch_id
    assert rv1.get_json()['result']['branch_id'] == str(branch.id)
    assert rv2.get_json()['result']['branch_id'] == str(branch.id)

    # List all patrons
    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Patrons.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    assert rv.get_json()['result']['count'] == 2


def test_patrons_activate_success(client: FlaskClient) -> None:
    """Test activating a patron successfully."""
    patron = PatronFactory(name='Inactive Patron', email='inactive@test.com', status=PatronStatus.SUSPENDED)

    params = {'patron_id': str(patron.id)}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Patrons.activate', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(patron.id)
    assert rv_data['result']['status'] == PatronStatus.ACTIVE.value


def test_patrons_activate_not_found(client: FlaskClient) -> None:
    """Test activating a non-existent patron."""
    fake_id = str(uuid.uuid7())

    params = {'patron_id': fake_id}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Patrons.activate', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_patrons_archive_success(client: FlaskClient) -> None:
    """Test archiving a patron successfully."""
    patron = PatronFactory(name='Active Patron', email='active@test.com', status=PatronStatus.ACTIVE)

    params = {'patron_id': str(patron.id)}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Patrons.archive', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(patron.id)
    assert rv_data['result']['status'] == PatronStatus.ARCHIVED.value


def test_patrons_archive_not_found(client: FlaskClient) -> None:
    """Test archiving a non-existent patron."""
    fake_id = str(uuid.uuid7())

    params = {'patron_id': fake_id}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Patrons.archive', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_fines_list_empty(client: FlaskClient) -> None:
    """Test listing fines when none exist."""
    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Fines.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_fines_list_with_fines(client: FlaskClient) -> None:
    """Test listing fines when multiple exist."""
    patron1 = PatronFactory(name='Patron One', email='patron1@test.com')
    patron2 = PatronFactory(name='Patron Two', email='patron2@test.com')
    FineFactory(patron=patron1, amount=Decimal('15.00'), reason='Late return')
    FineFactory(patron=patron2, amount=Decimal('25.50'), reason='Lost book')

    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Fines.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_fines_get_success(client: FlaskClient) -> None:
    """Test getting a fine by ID successfully."""
    patron = PatronFactory(name='Patron', email='patron@test.com')
    fine = FineFactory(patron=patron, amount=Decimal('20.00'), reason='Overdue fine', status=FineStatus.UNPAID)

    params = {'fine_id': str(fine.id)}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.get', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(fine.id)
    assert rv_data['result']['patron_id'] == str(patron.id)
    assert rv_data['result']['amount'] == '20.00'


def test_fines_get_not_found(client: FlaskClient) -> None:
    """Test getting a non-existent fine."""
    fake_id = str(uuid.uuid7())

    params = {'fine_id': fake_id}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.get', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_fines_pay_success(client: FlaskClient) -> None:
    """Test paying a fine successfully."""
    patron = PatronFactory(name='Patron', email='patron@test.com')
    fine = FineFactory(patron=patron, amount=Decimal('30.00'), reason='Damaged book', status=FineStatus.UNPAID)

    params = {'fine_id': str(fine.id)}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.pay', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(fine.id)
    assert rv_data['result']['status'] == FineStatus.PAID.value
    assert rv_data['result']['paid_date'] is not None


def test_fines_pay_not_found(client: FlaskClient) -> None:
    """Test paying a non-existent fine."""
    fake_id = str(uuid.uuid7())

    params = {'fine_id': fake_id}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.pay', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_fines_pay_already_paid(client: FlaskClient) -> None:
    """Test paying a fine that is already paid."""
    patron = PatronFactory(name='Patron', email='patron@test.com')
    fine = FineFactory(patron=patron, amount=Decimal('10.00'), reason='Late fee', status=FineStatus.PAID)

    params = {'fine_id': str(fine.id)}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.pay', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_fines_waive_success(client: FlaskClient) -> None:
    """Test waiving a fine successfully."""
    patron = PatronFactory(name='Patron', email='patron@test.com')
    fine = FineFactory(patron=patron, amount=Decimal('15.00'), reason='Processing fee', status=FineStatus.UNPAID)

    params = {'fine_id': str(fine.id)}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.waive', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(fine.id)
    assert rv_data['result']['status'] == FineStatus.WAIVED.value
    assert rv_data['result']['paid_date'] is not None


def test_fines_waive_not_found(client: FlaskClient) -> None:
    """Test waiving a non-existent fine."""
    fake_id = str(uuid.uuid7())

    params = {'fine_id': fake_id}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.waive', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_fines_waive_already_waived(client: FlaskClient) -> None:
    """Test waiving a fine that is already waived."""
    patron = PatronFactory(name='Patron', email='patron@test.com')
    fine = FineFactory(patron=patron, amount=Decimal('5.00'), reason='Service charge', status=FineStatus.WAIVED)

    params = {'fine_id': str(fine.id)}
    rv = client.post(
        '/api/patrons', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.waive', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_patron_lifecycle_with_fines(client: FlaskClient) -> None:
    """Test complete patron lifecycle including fine management."""
    branch = BranchFactory(name='Central Library')
    patron = PatronFactory(branch=branch, name='Lifecycle Patron', email='lifecycle.patron@test.com')
    fine = FineFactory(patron=patron, amount=Decimal('25.00'), reason='Overdue book', status=FineStatus.UNPAID)

    # Get the fine
    rv = client.post(
        '/api/patrons',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.get', 'params': {'fine_id': str(fine.id)}},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == FineStatus.UNPAID.value

    # Pay the fine
    rv = client.post(
        '/api/patrons',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.pay', 'params': {'fine_id': str(fine.id)}},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == FineStatus.PAID.value

    # Archive patron
    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patrons.archive',
            'params': {'patron_id': str(patron.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == PatronStatus.ARCHIVED.value


def test_patron_status_transitions(client: FlaskClient) -> None:
    """Test patron status transitions: suspended -> active -> archived."""
    patron = PatronFactory(name='Status Test', email='status@test.com', status=PatronStatus.SUSPENDED)

    # Activate patron
    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patrons.activate',
            'params': {'patron_id': str(patron.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == PatronStatus.ACTIVE.value

    # Archive patron
    rv = client.post(
        '/api/patrons',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Patrons.archive',
            'params': {'patron_id': str(patron.id)},
        },
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == PatronStatus.ARCHIVED.value


def test_multiple_fines_for_single_patron(client: FlaskClient) -> None:
    """Test managing multiple fines for a single patron."""
    patron = PatronFactory(name='Multi Fine Patron', email='multifine@test.com')
    fine1 = FineFactory(patron=patron, amount=Decimal('10.00'), reason='Late return', status=FineStatus.UNPAID)
    fine2 = FineFactory(patron=patron, amount=Decimal('20.00'), reason='Damaged book', status=FineStatus.UNPAID)
    fine3 = FineFactory(patron=patron, amount=Decimal('5.00'), reason='Processing fee', status=FineStatus.UNPAID)

    # List all fines
    rv = client.post(
        '/api/patrons', json={'jsonrpc': '2.0', 'method': 'Fines.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['count'] == 3

    # Pay first fine
    rv = client.post(
        '/api/patrons',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.pay', 'params': {'fine_id': str(fine1.id)}},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == FineStatus.PAID.value

    # Waive second fine
    rv = client.post(
        '/api/patrons',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.waive', 'params': {'fine_id': str(fine2.id)}},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == FineStatus.WAIVED.value

    # Third fine remains unpaid
    rv = client.post(
        '/api/patrons',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Fines.get', 'params': {'fine_id': str(fine3.id)}},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['status'] == FineStatus.UNPAID.value
