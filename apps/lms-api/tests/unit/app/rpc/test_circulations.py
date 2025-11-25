from __future__ import annotations

import uuid
import datetime

from flask.testing import FlaskClient

from tests.unit.factories import CopyFactory, HoldFactory, ItemFactory, LoanFactory, StaffFactory, PatronFactory
from lms.infrastructure.database.models.patrons import PatronStatus
from lms.infrastructure.database.models.catalogs import CopyStatus
from lms.infrastructure.database.models.circulations import HoldStatus


def test_loans_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/circulations', json={'jsonrpc': '2.0', 'method': 'Loans.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_loans_list_with_loans(client: FlaskClient) -> None:
    LoanFactory()
    LoanFactory()

    rv = client.post(
        '/api/circulations', json={'jsonrpc': '2.0', 'method': 'Loans.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_loans_checkout_copy_success(client: FlaskClient) -> None:
    patron = PatronFactory()
    copy = CopyFactory(status=CopyStatus.AVAILABLE)
    staff = StaffFactory()

    params = {'patron_id': str(patron.id), 'copy_id': str(copy.id), 'staff_id': str(staff.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkout_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    loan = rv_data['result']
    assert loan['patron_id'] == str(patron.id)
    assert loan['copy_id'] == str(copy.id)
    assert loan['staff_out_id'] == str(staff.id)
    assert loan['return_date'] is None


def test_loans_checkout_copy_patron_not_found(client: FlaskClient) -> None:
    fake_patron_id = str(uuid.uuid7())
    copy = CopyFactory(status=CopyStatus.AVAILABLE)
    staff = StaffFactory()

    params = {'patron_id': fake_patron_id, 'copy_id': str(copy.id), 'staff_id': str(staff.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkout_copy', 'params': params},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_loans_checkout_copy_copy_not_found(client: FlaskClient) -> None:
    patron = PatronFactory()
    fake_copy_id = str(uuid.uuid7())
    staff = StaffFactory()

    params = {'patron_id': str(patron.id), 'copy_id': fake_copy_id, 'staff_id': str(staff.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkout_copy', 'params': params},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_loans_checkout_copy_staff_not_found(client: FlaskClient) -> None:
    patron = PatronFactory()
    copy = CopyFactory(status=CopyStatus.AVAILABLE)
    fake_staff_id = str(uuid.uuid7())

    params = {'patron_id': str(patron.id), 'copy_id': str(copy.id), 'staff_id': fake_staff_id}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkout_copy', 'params': params},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_loans_checkin_copy_success(client: FlaskClient) -> None:
    copy = CopyFactory(status=CopyStatus.CHECKED_OUT)
    loan = LoanFactory(copy=copy, return_date=None)
    staff = StaffFactory()

    params = {'loan_id': str(loan.id), 'staff_id': str(staff.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkin_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    result = rv_data['result']
    assert result['id'] == str(loan.id)
    assert result['return_date'] is not None


def test_loans_checkin_copy_loan_not_found(client: FlaskClient) -> None:
    fake_loan_id = str(uuid.uuid7())
    staff = StaffFactory()

    params = {'loan_id': fake_loan_id, 'staff_id': str(staff.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkin_copy', 'params': params},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_loans_damaged_copy_success(client: FlaskClient) -> None:
    loan = LoanFactory()

    params = {'loan_id': str(loan.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.damaged_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(loan.id)


def test_loans_damaged_copy_not_found(client: FlaskClient) -> None:
    fake_loan_id = str(uuid.uuid7())

    params = {'loan_id': fake_loan_id}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.damaged_copy', 'params': params},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_loans_lost_copy_success(client: FlaskClient) -> None:
    loan = LoanFactory()

    params = {'loan_id': str(loan.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.lost_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(loan.id)


def test_loans_lost_copy_not_found(client: FlaskClient) -> None:
    fake_loan_id = str(uuid.uuid7())

    params = {'loan_id': fake_loan_id}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.lost_copy', 'params': params},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_loans_get_success(client: FlaskClient) -> None:
    loan = LoanFactory()

    params = {'loan_id': str(loan.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.get', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(loan.id)


def test_loans_get_not_found(client: FlaskClient) -> None:
    fake_loan_id = str(uuid.uuid7())

    params = {'loan_id': fake_loan_id}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.get', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_loans_renew_success(client: FlaskClient) -> None:
    patron = PatronFactory(status=PatronStatus.ACTIVE)
    loan = LoanFactory(patron=patron, return_date=None, due_date=datetime.date.today() + datetime.timedelta(days=7))

    params = {'loan_id': str(loan.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.renew', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(loan.id)


def test_loans_renew_not_found(client: FlaskClient) -> None:
    fake_loan_id = str(uuid.uuid7())

    params = {'loan_id': fake_loan_id}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.renew', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_holds_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/circulations', json={'jsonrpc': '2.0', 'method': 'Holds.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_holds_list_with_holds(client: FlaskClient) -> None:
    HoldFactory()
    HoldFactory()

    rv = client.post(
        '/api/circulations', json={'jsonrpc': '2.0', 'method': 'Holds.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    rv_data = rv.get_json()
    assert rv.status_code == 200, rv_data
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_holds_get_success(client: FlaskClient) -> None:
    hold = HoldFactory()

    params = {'hold_id': str(hold.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.get', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(hold.id)


def test_holds_get_not_found(client: FlaskClient) -> None:
    fake_hold_id = str(uuid.uuid7())

    params = {'hold_id': fake_hold_id}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.get', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_holds_place_success(client: FlaskClient) -> None:
    patron = PatronFactory()
    item = ItemFactory()

    params = {'patron_id': str(patron.id), 'item_id': str(item.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.place', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    hold = rv_data['result']
    assert hold['patron_id'] == str(patron.id)
    assert hold['status'] == 'pending'


def test_holds_place_with_copy(client: FlaskClient) -> None:
    patron = PatronFactory()
    item = ItemFactory()
    copy = CopyFactory(item=item)

    params = {'patron_id': str(patron.id), 'item_id': str(item.id), 'copy_id': str(copy.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.place', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    hold = rv_data['result']
    assert hold['patron_id'] == str(patron.id)
    assert hold['copy_id'] == str(copy.id)


def test_holds_place_patron_not_found(client: FlaskClient) -> None:
    fake_patron_id = str(uuid.uuid7())
    item = ItemFactory()

    params = {'patron_id': fake_patron_id, 'item_id': str(item.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.place', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_holds_place_item_not_found(client: FlaskClient) -> None:
    patron = PatronFactory()
    fake_item_id = str(uuid.uuid7())

    params = {'patron_id': str(patron.id), 'item_id': fake_item_id}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.place', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_holds_pickup_success(client: FlaskClient) -> None:
    hold = HoldFactory(status=HoldStatus.PENDING)
    staff = StaffFactory()
    copy = CopyFactory(status=CopyStatus.AVAILABLE)

    params = {'hold_id': str(hold.id), 'staff_id': str(staff.id), 'copy_id': str(copy.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.pickup', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    loan = rv_data['result']
    assert loan['patron_id'] == str(hold.patron_id)
    assert loan['copy_id'] == str(copy.id)


def test_holds_pickup_hold_not_found(client: FlaskClient) -> None:
    fake_hold_id = str(uuid.uuid7())
    staff = StaffFactory()
    copy = CopyFactory()

    params = {'hold_id': fake_hold_id, 'staff_id': str(staff.id), 'copy_id': str(copy.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.pickup', 'params': params},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_holds_cancel_success(client: FlaskClient) -> None:
    hold = HoldFactory(status=HoldStatus.PENDING)

    params = {'hold_id': str(hold.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.cancel', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    result = rv_data['result']
    assert result['id'] == str(hold.id)
    assert result['status'] == 'cancelled'


def test_holds_cancel_not_found(client: FlaskClient) -> None:
    fake_hold_id = str(uuid.uuid7())

    params = {'hold_id': fake_hold_id}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.cancel', 'params': params},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_complete_circulation_workflow(client: FlaskClient) -> None:
    patron = PatronFactory()
    item = ItemFactory()
    copy = CopyFactory(item_id=item.id, status=CopyStatus.AVAILABLE)
    staff = StaffFactory()

    # Place hold
    params = {'patron_id': str(patron.id), 'item_id': str(item.id), 'copy_id': str(copy.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.place', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    hold_id = rv.get_json()['result']['id']

    # Pickup hold
    params = {'hold_id': hold_id, 'staff_id': str(staff.id), 'copy_id': str(copy.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.pickup', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    loan_id = rv.get_json()['result']['id']

    # Renew loan
    params = {'loan_id': loan_id}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.renew', 'params': params}
    )
    assert rv.status_code == 200, rv.data

    # Checkin copy
    params = {'loan_id': loan_id, 'staff_id': str(staff.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkin_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['return_date'] is not None


def test_checkout_and_return_workflow(client: FlaskClient) -> None:
    patron = PatronFactory()
    copy = CopyFactory(status=CopyStatus.AVAILABLE)
    staff = StaffFactory()

    # Checkout
    params = {'patron_id': str(patron.id), 'copy_id': str(copy.id), 'staff_id': str(staff.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkout_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    loan_id = rv.get_json()['result']['id']

    # Return
    params = {'loan_id': loan_id, 'staff_id': str(staff.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.checkin_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data
    result = rv.get_json()['result']
    assert result['return_date'] is not None
    assert result['staff_in_id'] == str(staff.id)


def test_multiple_holds_on_same_item(client: FlaskClient) -> None:
    item = ItemFactory()
    patron1 = PatronFactory()
    patron2 = PatronFactory()

    # First hold
    params = {'patron_id': str(patron1.id), 'item_id': str(item.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.place', 'params': params}
    )
    assert rv.status_code == 200, rv.data

    # Second hold
    params = {'patron_id': str(patron2.id), 'item_id': str(item.id)}
    rv = client.post(
        '/api/circulations', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Holds.place', 'params': params}
    )
    assert rv.status_code == 200, rv.data

    # List all holds
    rv = client.post(
        '/api/circulations', json={'jsonrpc': '2.0', 'method': 'Holds.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    assert rv.get_json()['result']['count'] == 2


def test_damaged_and_lost_copy_handling(client: FlaskClient) -> None:
    loan1 = LoanFactory(return_date=None)
    loan2 = LoanFactory(return_date=None)

    # Mark first copy as damaged
    params = {'loan_id': str(loan1.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.damaged_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data

    # Mark second copy as lost
    params = {'loan_id': str(loan2.id)}
    rv = client.post(
        '/api/circulations',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Loans.lost_copy', 'params': params},
    )
    assert rv.status_code == 200, rv.data

    # Verify both loans still exist
    rv = client.post(
        '/api/circulations', json={'jsonrpc': '2.0', 'method': 'Loans.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    assert rv.get_json()['result']['count'] == 2
