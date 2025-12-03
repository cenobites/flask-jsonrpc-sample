from __future__ import annotations

import uuid
import typing as t

from flask import Flask, current_app

from lms.app.services.catalogs import ItemService
from lms.infrastructure.logging import logger
from lms.infrastructure.event_bus import event_bus
from lms.app.services.organizations import StaffService
from lms.domain.acquisitions.events import AcquisitionOrderReceivedEvent


def handle_acquisition_order_received(event: AcquisitionOrderReceivedEvent) -> None:
    logger.info('Acquisition order received: ID=%s', event.acquisition_order_id)
    item_service: ItemService = current_app.container.item_service  # type: ignore
    staff_service: StaffService = current_app.container.staff_service  # type: ignore
    staff = staff_service.get_staff(event.staff_id)
    logger.info('Processing received items for staff ID=%s at branch ID=%s', staff.id, staff.branch_id)
    for item_id, quantity in event.item_lines:
        for _ in range(quantity):
            barcode = f'BC-{str(uuid.uuid4())}'
            copy = item_service.add_copy_to_item(
                item_id=item_id,
                branch_id=t.cast(str, staff.branch_id),
                barcode=barcode,
                acquisition_date=event.acquisition_date,
            )
            logger.info('New copy added: CopyID=%s, ItemID=%s, Barcode=%s', copy.id, copy.item_id, copy.barcode)


def register_handler(app: Flask) -> None:
    event_bus.subscribe(AcquisitionOrderReceivedEvent, handle_acquisition_order_received)
