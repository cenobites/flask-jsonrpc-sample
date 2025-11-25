from __future__ import annotations


class CopyNotAvailable(Exception):
    def __init__(self, copy_id: str, /) -> None:
        super().__init__(f'Copy {copy_id} is not available for loan')
        self.copy_id = copy_id


class CopyNotCheckedOut(Exception):
    def __init__(self, copy_id: str, /) -> None:
        super().__init__(f'Copy {copy_id} is not checked out')
        self.copy_id = copy_id


class CopyAlreadyCheckedOut(Exception):
    def __init__(self, copy_id: str, /) -> None:
        super().__init__(f'Copy {copy_id} is already checked out')
        self.copy_id = copy_id


class CopyAlreadyLost(Exception):
    def __init__(self, copy_id: str, /) -> None:
        super().__init__(f'Copy {copy_id} is already marked as lost')
        self.copy_id = copy_id


class CopyAlreadyDamaged(Exception):
    def __init__(self, copy_id: str, /) -> None:
        super().__init__(f'Copy {copy_id} is already marked as damaged')
        self.copy_id = copy_id
