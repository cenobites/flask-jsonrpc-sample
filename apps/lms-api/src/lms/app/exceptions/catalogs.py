from . import ObjectNotFoundFailed


class ItemNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Item not found')


class CopyNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Copy not found')


class CategoryNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Category not found')


class AuthorNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Author not found')


class PublisherNotFoundError(ObjectNotFoundFailed):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message=message or 'Publisher not found')
