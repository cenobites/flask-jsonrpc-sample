from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import MagicMock, patch

from flask import Flask

from lms.app.handlers.catalogs import register_handler, handle_acquisition_order_received
from lms.domain.acquisitions.events import AcquisitionOrderReceivedEvent


def test_handle_acquisition_order_received_creates_copies(app: Flask) -> None:
    # Setup mock services
    mock_item_service = MagicMock()
    mock_staff_service = MagicMock()

    # Mock staff with branch
    mock_staff = MagicMock()
    mock_staff.id = str(uuid.uuid4())
    mock_staff.branch_id = str(uuid.uuid4())
    mock_staff_service.get_staff.return_value = mock_staff

    # Mock copy creation
    mock_copy = MagicMock()
    mock_copy.id = str(uuid.uuid4())
    mock_copy.item_id = str(uuid.uuid4())
    mock_copy.barcode = f'BC-{str(uuid.uuid4())}'
    mock_item_service.add_copy_to_item.return_value = mock_copy

    # Inject mocks into container
    mock_container = MagicMock()
    mock_container.item_service = mock_item_service
    mock_container.staff_service = mock_staff_service
    app.container = mock_container  # type: ignore

    # Create event with multiple items
    item_id_1 = str(uuid.uuid4())
    item_id_2 = str(uuid.uuid4())
    event = AcquisitionOrderReceivedEvent(
        acquisition_order_id=str(uuid.uuid4()),
        vendor_id=str(uuid.uuid4()),
        staff_id=mock_staff.id,
        item_lines=[(item_id_1, 2), (item_id_2, 1)],
        acquisition_date=date.today(),
    )

    # Handle the event
    handle_acquisition_order_received(event)

    # Verify staff was retrieved
    mock_staff_service.get_staff.assert_called_once_with(event.staff_id)

    # Verify copies were created (2 for item_id_1, 1 for item_id_2)
    assert mock_item_service.add_copy_to_item.call_count == 3

    # Verify first item copies
    calls = mock_item_service.add_copy_to_item.call_args_list
    assert calls[0].kwargs['item_id'] == item_id_1
    assert calls[0].kwargs['branch_id'] == mock_staff.branch_id
    assert calls[0].kwargs['acquisition_date'] == event.acquisition_date
    assert calls[0].kwargs['barcode'].startswith('BC-')

    assert calls[1].kwargs['item_id'] == item_id_1
    assert calls[1].kwargs['branch_id'] == mock_staff.branch_id

    # Verify second item copy
    assert calls[2].kwargs['item_id'] == item_id_2
    assert calls[2].kwargs['branch_id'] == mock_staff.branch_id


def test_handle_acquisition_order_received_single_item_single_quantity(app: Flask) -> None:
    mock_item_service = MagicMock()
    mock_staff_service = MagicMock()

    mock_staff = MagicMock()
    mock_staff.id = str(uuid.uuid4())
    mock_staff.branch_id = str(uuid.uuid4())
    mock_staff_service.get_staff.return_value = mock_staff

    mock_copy = MagicMock()
    mock_copy.id = str(uuid.uuid4())
    mock_item_service.add_copy_to_item.return_value = mock_copy

    # Inject mocks into container
    mock_container = MagicMock()
    mock_container.item_service = mock_item_service
    mock_container.staff_service = mock_staff_service
    app.container = mock_container  # type: ignore

    item_id = str(uuid.uuid4())
    event = AcquisitionOrderReceivedEvent(
        acquisition_order_id=str(uuid.uuid4()),
        vendor_id=str(uuid.uuid4()),
        staff_id=mock_staff.id,
        item_lines=[(item_id, 1)],
        acquisition_date=date.today(),
    )

    handle_acquisition_order_received(event)

    # Verify only one copy was created
    assert mock_item_service.add_copy_to_item.call_count == 1
    mock_item_service.add_copy_to_item.assert_called_once()


def test_handle_acquisition_order_received_empty_items(app: Flask) -> None:
    mock_item_service = MagicMock()
    mock_staff_service = MagicMock()

    mock_staff = MagicMock()
    mock_staff.id = str(uuid.uuid4())
    mock_staff.branch_id = str(uuid.uuid4())
    mock_staff_service.get_staff.return_value = mock_staff

    # Inject mocks into container
    mock_container = MagicMock()
    mock_container.item_service = mock_item_service
    mock_container.staff_service = mock_staff_service
    app.container = mock_container  # type: ignore

    event = AcquisitionOrderReceivedEvent(
        acquisition_order_id=str(uuid.uuid4()),
        vendor_id=str(uuid.uuid4()),
        staff_id=mock_staff.id,
        item_lines=[],
        acquisition_date=date.today(),
    )

    handle_acquisition_order_received(event)

    # Verify no copies were created
    mock_item_service.add_copy_to_item.assert_not_called()


def test_handle_acquisition_order_received_generates_unique_barcodes(app: Flask) -> None:
    mock_item_service = MagicMock()
    mock_staff_service = MagicMock()

    mock_staff = MagicMock()
    mock_staff.id = str(uuid.uuid4())
    mock_staff.branch_id = str(uuid.uuid4())
    mock_staff_service.get_staff.return_value = mock_staff

    mock_copy = MagicMock()
    mock_item_service.add_copy_to_item.return_value = mock_copy

    # Inject mocks into container
    mock_container = MagicMock()
    mock_container.item_service = mock_item_service
    mock_container.staff_service = mock_staff_service
    app.container = mock_container  # type: ignore

    item_id = str(uuid.uuid4())
    event = AcquisitionOrderReceivedEvent(
        acquisition_order_id=str(uuid.uuid4()),
        vendor_id=str(uuid.uuid4()),
        staff_id=mock_staff.id,
        item_lines=[(item_id, 3)],
        acquisition_date=date.today(),
    )

    handle_acquisition_order_received(event)

    # Get all barcodes
    barcodes = [call.kwargs['barcode'] for call in mock_item_service.add_copy_to_item.call_args_list]

    # Verify all barcodes are unique
    assert len(barcodes) == 3
    assert len(set(barcodes)) == 3

    # Verify all barcodes have correct format
    for barcode in barcodes:
        assert barcode.startswith('BC-')


@patch('lms.app.handlers.catalogs.event_bus')
def test_register_handler_subscribes_to_event(mock_event_bus: MagicMock, app: Flask) -> None:
    register_handler(app)

    mock_event_bus.subscribe.assert_called_once_with(AcquisitionOrderReceivedEvent, handle_acquisition_order_received)


def test_handle_acquisition_order_received_uses_correct_acquisition_date(app: Flask) -> None:
    mock_item_service = MagicMock()
    mock_staff_service = MagicMock()

    mock_staff = MagicMock()
    mock_staff.id = str(uuid.uuid4())
    mock_staff.branch_id = str(uuid.uuid4())
    mock_staff_service.get_staff.return_value = mock_staff

    mock_copy = MagicMock()
    mock_item_service.add_copy_to_item.return_value = mock_copy

    # Inject mocks into container
    mock_container = MagicMock()
    mock_container.item_service = mock_item_service
    mock_container.staff_service = mock_staff_service
    app.container = mock_container  # type: ignore

    acquisition_date = date(2025, 1, 15)
    event = AcquisitionOrderReceivedEvent(
        acquisition_order_id=str(uuid.uuid4()),
        vendor_id=str(uuid.uuid4()),
        staff_id=mock_staff.id,
        item_lines=[(str(uuid.uuid4()), 1)],
        acquisition_date=acquisition_date,
    )

    handle_acquisition_order_received(event)

    # Verify acquisition date was passed correctly
    call_kwargs = mock_item_service.add_copy_to_item.call_args.kwargs
    assert call_kwargs['acquisition_date'] == acquisition_date
