from . import ObjectNotFoundFailed


class AcquisitionOrderNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Acquisition order not found')


class AcquisitionOrderLineNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Acquisition order line not found')


class VendorNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Vendor not found')
