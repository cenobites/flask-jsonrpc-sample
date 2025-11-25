from __future__ import annotations

from lms.domain import DomainError


class AcquisitionOrderNotPending(DomainError):
    def __init__(self, order_id: str, /) -> None:
        super().__init__(f'Acquisition order {order_id} is not pending')
        self.order_id = order_id


class AcquisitionOrderHasNoLines(DomainError):
    def __init__(self, order_id: str, /) -> None:
        super().__init__(f'Acquisition order {order_id} has no order lines')
        self.order_id = order_id


class AcquisitionOrderAlreadySubmitted(DomainError):
    def __init__(self, order_id: str, /) -> None:
        super().__init__(f'Acquisition order {order_id} is already submitted')
        self.order_id = order_id


class AcquisitionOrderLineAlreadyReceived(DomainError):
    def __init__(self, order_line_id: str, order_id: str, /) -> None:
        super().__init__(
            f'Acquisition order line {order_line_id} from acquisition order {order_id} is already received'
        )
        self.order_line_id = order_line_id
        self.order_id = order_id


class AcquisitionOrderLineNotSubmitted(DomainError):
    def __init__(self, order_line_id: str, order_id: str, /) -> None:
        super().__init__(f'Acquisition order line {order_line_id} from acquisition order {order_id} is not submitted')
        self.order_line_id = order_line_id
        self.order_id = order_id


class VendorAlreadyActive(DomainError):
    def __init__(self, vendor_id: str, /) -> None:
        super().__init__(f'Vendor {vendor_id} is already active')
        self.vendor_id = vendor_id


class VendorAlreadyInactive(DomainError):
    def __init__(self, vendor_id: str, /) -> None:
        super().__init__(f'Vendor {vendor_id} is already inactive')
        self.vendor_id = vendor_id
