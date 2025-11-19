from __future__ import annotations

from flask.testing import FlaskClient


def test_health(client: FlaskClient) -> None:
    rv = client.get('/monitoring/health')
    assert rv.status_code == 200
    rv_data = rv.get_json()
    assert rv_data == {'status': 'OK'}
