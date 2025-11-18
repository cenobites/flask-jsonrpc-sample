from __future__ import annotations

import uuid

from flask.testing import FlaskClient

from .factories import ItemFactory, SerialFactory


def test_serial_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/serial', json={'jsonrpc': '2.0', 'method': 'Serial.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_serial_list_with_serials(client: FlaskClient) -> None:
    SerialFactory(title='Journal of Science', issn='1234-5678')
    SerialFactory(title='Tech Magazine', issn='8765-4321')

    rv = client.post(
        '/api/serial', json={'jsonrpc': '2.0', 'method': 'Serial.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_serial_create_minimal(client: FlaskClient) -> None:
    item = ItemFactory(title='Serial Item')

    params = {'serial': {'title': 'Science Weekly', 'issn': '1111-2222', 'item_id': str(item.id)}}
    rv = client.post(
        '/api/serial', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    serial = rv_data['result']
    assert serial['title'] == 'Science Weekly'
    assert serial['issn'] == '1111-2222'
    assert serial['item_id'] == str(item.id)
    assert serial['status'] == 'active'


def test_serial_create_with_all_fields(client: FlaskClient) -> None:
    item = ItemFactory(title='Serial Item Full')

    params = {
        'serial': {
            'title': 'Complete Journal',
            'issn': '3333-4444',
            'item_id': str(item.id),
            'frequency': 'monthly',
            'description': 'A comprehensive scientific journal',
        }
    }
    rv = client.post(
        '/api/serial', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    serial = rv_data['result']
    assert serial['title'] == 'Complete Journal'
    assert serial['issn'] == '3333-4444'
    assert serial['frequency'] == 'monthly'
    assert serial['description'] == 'A comprehensive scientific journal'


def test_serial_create_item_not_found(client: FlaskClient) -> None:
    fake_item_id = str(uuid.uuid7())

    params = {'serial': {'title': 'Failed Serial', 'issn': '9999-0000', 'item_id': fake_item_id}}
    rv = client.post(
        '/api/serial', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.create', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_serial_get_success(client: FlaskClient) -> None:
    serial = SerialFactory(title='Test Serial', issn='5555-6666')

    params = {'serial_id': str(serial.id)}
    rv = client.post(
        '/api/serial', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.get', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(serial.id)
    assert rv_data['result']['title'] == 'Test Serial'
    assert rv_data['result']['issn'] == '5555-6666'


def test_serial_get_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/serial',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.get', 'params': {'serial_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_complete_serial_workflow(client: FlaskClient) -> None:
    item = ItemFactory(title='Workflow Serial Item')

    # Create serial
    params = {
        'serial': {
            'title': 'Workflow Journal',
            'issn': '7777-8888',
            'item_id': str(item.id),
            'frequency': 'weekly',
            'description': 'A test workflow journal',
        }
    }
    rv = client.post(
        '/api/serial', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    serial_id = rv.get_json()['result']['id']

    # Get the serial
    rv = client.post(
        '/api/serial',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.get', 'params': {'serial_id': serial_id}},
    )
    assert rv.status_code == 200, rv.data
    result = rv.get_json()['result']
    assert result['title'] == 'Workflow Journal'
    assert result['issn'] == '7777-8888'
    assert result['frequency'] == 'weekly'
    assert result['description'] == 'A test workflow journal'


def test_create_multiple_serials(client: FlaskClient) -> None:
    item1 = ItemFactory(title='Journal Item 1')
    item2 = ItemFactory(title='Magazine Item 2')

    # Create first serial
    params = {
        'serial': {'title': 'First Journal', 'issn': '1000-1000', 'item_id': str(item1.id), 'frequency': 'monthly'}
    }
    rv = client.post(
        '/api/serial', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data

    # Create second serial
    params = {
        'serial': {'title': 'Second Magazine', 'issn': '2000-2000', 'item_id': str(item2.id), 'frequency': 'weekly'}
    }
    rv = client.post(
        '/api/serial', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data

    # List all serials
    rv = client.post(
        '/api/serial', json={'jsonrpc': '2.0', 'method': 'Serial.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    assert rv.get_json()['result']['count'] == 2


def test_serial_creation_and_retrieval(client: FlaskClient) -> None:
    item = ItemFactory(title='Retrieval Test Item')

    params = {
        'serial': {
            'title': 'Retrieval Test Serial',
            'issn': '4000-4000',
            'item_id': str(item.id),
            'description': 'A test serial for retrieval',
        }
    }
    rv = client.post(
        '/api/serial', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    serial_id = rv.get_json()['result']['id']

    # Get the serial
    rv = client.post(
        '/api/serial',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Serial.get', 'params': {'serial_id': serial_id}},
    )
    assert rv.status_code == 200, rv.data
    result = rv.get_json()['result']
    assert result['title'] == 'Retrieval Test Serial'
    assert result['issn'] == '4000-4000'
    assert result['description'] == 'A test serial for retrieval'
    assert result['status'] == 'active'


def test_serial_list_pagination(client: FlaskClient) -> None:
    SerialFactory(title='Serial A', issn='0001-0001')
    SerialFactory(title='Serial B', issn='0002-0002')
    SerialFactory(title='Serial C', issn='0003-0003')

    rv = client.post(
        '/api/serial', json={'jsonrpc': '2.0', 'method': 'Serial.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 3
    results = rv_data['result']['results']
    assert len(results) == 3
    titles = [r['title'] for r in results]
    assert 'Serial A' in titles
    assert 'Serial B' in titles
    assert 'Serial C' in titles
