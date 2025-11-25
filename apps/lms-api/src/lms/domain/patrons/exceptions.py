from __future__ import annotations

from lms.domain import DomainError


class PatronEmailAlreadyExists(DomainError):
    def __init__(self, email: str, /) -> None:
        super().__init__(f'Patron with email {email!r} already exists')
        self.email = email


class PatronAlreadyActive(DomainError):
    def __init__(self, patron_id: str, /) -> None:
        super().__init__(f'Patron {patron_id} is already active')
        self.patron_id = patron_id


class PatronNotActive(DomainError):
    def __init__(self, patron_id: str, /) -> None:
        super().__init__(f'Patron {patron_id} is not active')
        self.patron_id = patron_id


class PatronNotArchived(DomainError):
    def __init__(self, patron_id: str, /) -> None:
        super().__init__(f'Patron {patron_id} is not archived')
        self.patron_id = patron_id


class PatronNotSuspended(DomainError):
    def __init__(self, patron_id: str, /) -> None:
        super().__init__(f'Patron {patron_id} is not suspended')
        self.patron_id = patron_id


class PatronHasActiveLoans(DomainError):
    def __init__(self, patron_id: str, /) -> None:
        super().__init__(f'Patron {patron_id} has active loans')
        self.patron_id = patron_id


class PatronHasNotActiveLoans(DomainError):
    def __init__(self, patron_id: str, /) -> None:
        super().__init__(f'Patron {patron_id} has not active loans')
        self.patron_id = patron_id


class PatronHasNotActiveHolds(DomainError):
    def __init__(self, patron_id: str, /) -> None:
        super().__init__(f'Patron {patron_id} has not active holds')
        self.patron_id = patron_id


class FineAlreadyPaid(DomainError):
    def __init__(self, patron_id: str, loan_id: str, /) -> None:
        super().__init__(f'Fine for patron {patron_id} and loan {loan_id} is already paid')
        self.patron_id = patron_id
        self.loan_id = loan_id


class FineAAlreadyWaived(DomainError):
    def __init__(self, patron_id: str, loan_id: str, /) -> None:
        super().__init__(f'Fine for patron {patron_id} and loan {loan_id} is already waived')
        self.patron_id = patron_id
        self.loan_id = loan_id
