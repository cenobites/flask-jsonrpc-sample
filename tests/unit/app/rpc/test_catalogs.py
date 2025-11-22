from __future__ import annotations

import uuid

from flask.testing import FlaskClient

from ...factories import CopyFactory, ItemFactory, BranchFactory


def test_item_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/catalogs', json={'jsonrpc': '2.0', 'method': 'Items.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_item_list_with_items(client: FlaskClient) -> None:
    ItemFactory(title='Item 1')
    ItemFactory(title='Item 2')

    rv = client.post(
        '/api/catalogs', json={'jsonrpc': '2.0', 'method': 'Items.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_item_create_minimal(client: FlaskClient) -> None:
    rv = client.post(
        '/api/catalogs',
        json={
            'id': str(uuid.uuid4()),
            'jsonrpc': '2.0',
            'method': 'Items.create',
            'params': {'item': {'barcode': 'ITM-001', 'title': 'Test Book', 'format': 'book'}},
        },
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    item = rv_data['result']
    assert item['title'] == 'Test Book'
    assert item['format'] == 'book'


def test_item_create_with_all_fields(client: FlaskClient) -> None:
    params = {
        'item': {
            'barcode': 'ITM-002',
            'title': 'Complete Book',
            'author': 'John Doe',
            'format': 'book',
            'isbn': '978-1234567890',
            'publication_year': 2023,
            'description': 'A complete book with all fields',
        }
    }
    rv = client.post(
        '/api/catalogs', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    item = rv_data['result']
    assert item['title'] == 'Complete Book'
    assert item['isbn'] == '978-1234567890'
    assert item['publication_year'] == 2023
    assert item['description'] == 'A complete book with all fields'


def test_item_get_success(client: FlaskClient) -> None:
    item = ItemFactory(title='Test Item', isbn='123-456')

    rv = client.post(
        '/api/catalogs',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.get', 'params': {'item_id': str(item.id)}},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(item.id)
    assert rv_data['result']['title'] == 'Test Item'
    assert rv_data['result']['isbn'] == '123-456'


def test_item_get_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/catalogs',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.get', 'params': {'item_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_item_update_title(client: FlaskClient) -> None:
    item = ItemFactory(title='Old Title')

    params = {'item': {'id': str(item.id), 'barcode': 'ITM-UPD', 'title': 'New Title', 'format': 'book'}}
    rv = client.post(
        '/api/catalogs', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.update', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['title'] == 'New Title', rv_data


def test_item_update_all_fields(client: FlaskClient) -> None:
    item = ItemFactory(title='Original Title')

    params = {
        'item_id': str(item.id),
        'item': {
            'id': str(item.id),
            'barcode': 'ITM-ALL',
            'title': 'Updated Title',
            'format': 'book',
            'isbn': '978-9876543210',
            'description': 'Updated description',
        },
    }
    rv = client.post(
        '/api/catalogs', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.update', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['title'] == 'Updated Title'
    assert rv_data['result']['isbn'] == '978-9876543210'
    assert rv_data['result']['description'] == 'Updated description'


def test_item_update_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    params = {'item_id': fake_id, 'item': {'id': fake_id, 'barcode': 'ITM-XXX', 'title': 'New Title', 'format': 'book'}}
    rv = client.post(
        '/api/catalogs', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.update', 'params': params}
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_copy_list_empty(client: FlaskClient) -> None:
    rv = client.post(
        '/api/catalogs', json={'jsonrpc': '2.0', 'method': 'Copies.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'jsonrpc': '2.0', 'id': rv_data['id'], 'result': {'count': 0, 'results': []}}


def test_copy_list_with_copies(client: FlaskClient) -> None:
    CopyFactory(barcode='COPY-001')
    CopyFactory(barcode='COPY-002')

    rv = client.post(
        '/api/catalogs', json={'jsonrpc': '2.0', 'method': 'Copies.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data['result']['count'] == 2
    assert len(rv_data['result']['results']) == 2


def test_copy_get_success(client: FlaskClient) -> None:
    copy = CopyFactory(barcode='COPY-GET')

    rv = client.post(
        '/api/catalogs',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Copies.get', 'params': {'copy_id': str(copy.id)}},
    )
    assert rv.status_code == 200, rv.data
    rv_data = rv.get_json()
    assert rv_data['result']['id'] == str(copy.id)
    assert rv_data['result']['barcode'] == 'COPY-GET'


def test_copy_get_not_found(client: FlaskClient) -> None:
    fake_id = str(uuid.uuid7())

    rv = client.post(
        '/api/catalogs',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Copies.get', 'params': {'copy_id': fake_id}},
    )
    assert rv.status_code == 500, rv.data
    rv_data = rv.get_json()
    assert 'error' in rv_data


def test_complete_catalog_workflow(client: FlaskClient) -> None:
    # Create item
    params = {
        'item': {
            'barcode': 'FLOW-ITM',
            'title': 'Workflow Book',
            'format': 'book',
            'isbn': '978-1111111111',
            'publication_year': 2024,
        }
    }

    rv = client.post(
        '/api/catalogs', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    item_id = rv.get_json()['result']['id']

    # Update item
    params = {'item': {'id': item_id, 'barcode': 'FLOW-ITM-UPD', 'title': 'Updated Workflow Book', 'format': 'book'}}
    rv = client.post(
        '/api/catalogs', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.update', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['title'] == 'Updated Workflow Book'

    # Verify item still exists
    rv = client.post(
        '/api/catalogs',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.get', 'params': {'item_id': item_id}},
    )
    assert rv.status_code == 200, rv.data
    assert rv.get_json()['result']['title'] == 'Updated Workflow Book'


def test_item_with_multiple_copies(client: FlaskClient) -> None:
    item = ItemFactory(title='Multi-Copy Book')
    branch1 = BranchFactory(name='Branch 1')
    branch2 = BranchFactory(name='Branch 2')
    CopyFactory(item=item, branch_id=str(branch1.id), barcode='MULTI-COPY-1')
    CopyFactory(item=item, branch_id=str(branch2.id), barcode='MULTI-COPY-2')

    # List all copies
    rv = client.post(
        '/api/catalogs', json={'jsonrpc': '2.0', 'method': 'Copies.list', 'params': {}, 'id': str(uuid.uuid4())}
    )
    assert rv.status_code == 200
    assert rv.get_json()['result']['count'] == 2


def test_item_creation_and_retrieval(client: FlaskClient) -> None:
    params = {
        'item': {
            'barcode': 'RETRIEVE-ITM',
            'title': 'Retrieval Test Book',
            'format': 'ebook',
            'description': 'A test book for retrieval',
        }
    }
    rv = client.post(
        '/api/catalogs', json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.create', 'params': params}
    )
    assert rv.status_code == 200, rv.data
    item_id = rv.get_json()['result']['id']

    # Get the item
    rv = client.post(
        '/api/catalogs',
        json={'id': str(uuid.uuid4()), 'jsonrpc': '2.0', 'method': 'Items.get', 'params': {'item_id': item_id}},
    )
    assert rv.status_code == 200, rv.data
    result = rv.get_json()['result']
    assert result['title'] == 'Retrieval Test Book'
    assert result['format'] == 'ebook'
    assert result['description'] == 'A test book for retrieval'
