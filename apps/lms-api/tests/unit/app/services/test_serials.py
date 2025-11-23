from __future__ import annotations

from unittest.mock import Mock, MagicMock

import pytest

from lms.app.services.serials import SerialService
from lms.domain.serials.entities import Serial
from lms.domain.catalogs.entities import Item


@pytest.fixture
def mock_serial_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_serial_issue_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def mock_item_repository() -> Mock:
    return MagicMock()


@pytest.fixture
def serial_service(
    mock_serial_repository: Mock, mock_serial_issue_repository: Mock, mock_item_repository: Mock
) -> SerialService:
    return SerialService(
        serial_repository=mock_serial_repository,
        serial_issue_repository=mock_serial_issue_repository,
        item_repository=mock_item_repository,
    )


def test_serial_service_find_all_serials(serial_service: SerialService, mock_serial_repository: Mock) -> None:
    mock_serials = [Mock(spec=Serial), Mock(spec=Serial)]
    mock_serial_repository.find_all.return_value = mock_serials

    result = serial_service.find_all_serials()

    assert result == mock_serials
    mock_serial_repository.find_all.assert_called_once()


def test_serial_service_get_serial_success(serial_service: SerialService, mock_serial_repository: Mock) -> None:
    serial = Mock(spec=Serial, id='serial-123')
    mock_serial_repository.get_by_id.return_value = serial

    result = serial_service.get_serial('serial-123')

    assert result == serial
    mock_serial_repository.get_by_id.assert_called_once_with('serial-123')


def test_serial_service_get_serial_not_found(serial_service: SerialService, mock_serial_repository: Mock) -> None:
    mock_serial_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Serial with id serial-999 not found'):
        serial_service.get_serial('serial-999')


def test_serial_service_subscribe_serial(
    serial_service: SerialService, mock_serial_repository: Mock, mock_item_repository: Mock
) -> None:
    item = Mock(spec=Item, id='item-123')
    serial = Mock(spec=Serial)
    mock_item_repository.get_by_id.return_value = item
    mock_serial_repository.save.return_value = serial

    result = serial_service.subscribe_serial(
        title='Nature Magazine', issn='0028-0836', item_id='item-123', frequency='Monthly'
    )

    assert result == serial
    mock_item_repository.get_by_id.assert_called_once_with('item-123')
    mock_serial_repository.save.assert_called_once()


def test_serial_service_subscribe_serial_minimal(
    serial_service: SerialService, mock_serial_repository: Mock, mock_item_repository: Mock
) -> None:
    item = Mock(spec=Item, id='item-123')
    serial = Mock(spec=Serial)
    mock_item_repository.get_by_id.return_value = item
    mock_serial_repository.save.return_value = serial

    result = serial_service.subscribe_serial(title='Science', issn='1234-5678', item_id='item-123')

    assert result == serial
    mock_serial_repository.save.assert_called_once()


def test_serial_service_subscribe_serial_item_not_found(
    serial_service: SerialService, mock_item_repository: Mock
) -> None:
    mock_item_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match='Item with id item-999 not found'):
        serial_service.subscribe_serial(title='Test', issn='1234', item_id='item-999')


def test_serial_service_renew_subscription(serial_service: SerialService, mock_serial_repository: Mock) -> None:
    serial = Mock(spec=Serial, id='serial-123')
    mock_serial_repository.get_by_id.return_value = serial
    mock_serial_repository.save.return_value = serial

    result = serial_service.renew_serial_subscription('serial-123')

    assert result == serial
    serial.activate.assert_called_once()


def test_serial_service_unsubscribe_serial(serial_service: SerialService, mock_serial_repository: Mock) -> None:
    serial = Mock(spec=Serial, id='serial-123')
    mock_serial_repository.get_by_id.return_value = serial
    mock_serial_repository.save.return_value = serial

    result = serial_service.unsubscribe_serial('serial-123')

    assert result == serial
    serial.deactivate.assert_called_once()
