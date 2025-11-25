from decimal import Decimal
from unittest.mock import Mock
from collections.abc import Iterator

import pytest

from lms.domain import DomainNotFound
from lms.domain.patrons.entities import Patron
from lms.domain.patrons.services import (
    FinePolicyService,
    PatronBarringService,
    PatronHoldingService,
    PatronUniquenessService,
    PatronReinstatementService,
)
from lms.domain.catalogs.entities import Copy, Item
from lms.domain.circulations.entities import Hold, Loan
from lms.infrastructure.database.models.patrons import PatronStatus
from lms.infrastructure.database.models.catalogs import ItemFormat


class TestPatronUniquenessService:
    @pytest.fixture
    def mock_patron_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_patron_repository: Iterator) -> Iterator:
        return PatronUniquenessService(patron_repository=mock_patron_repository)

    def test_is_email_unique_when_email_does_not_exist(self, service: object, mock_patron_repository: object) -> None:
        mock_patron_repository.exists_by_email.return_value = False

        result = service.is_email_unique('new@example.com')

        assert result is True
        mock_patron_repository.exists_by_email.assert_called_once_with('new@example.com')

    def test_is_email_unique_when_email_exists(self, service: object, mock_patron_repository: object) -> None:
        mock_patron_repository.exists_by_email.return_value = True

        result = service.is_email_unique('existing@example.com')

        assert result is False
        mock_patron_repository.exists_by_email.assert_called_once_with('existing@example.com')


class TestPatronBarringService:
    @pytest.fixture
    def mock_patron_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def mock_loan_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_patron_repository: Iterator, mock_loan_repository: Iterator) -> Iterator:
        return PatronBarringService(patron_repository=mock_patron_repository, loan_repository=mock_loan_repository)

    def test_can_borrow_copies_when_active_and_no_loans(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.ACTIVE.value
        mock_patron_repository.get_by_id.return_value = mock_patron
        mock_loan_repository.find_by_patron_id.return_value = []

        result = service.can_borrow_copies('p1')

        assert result is True

    def test_can_borrow_copies_when_patron_not_found(self, service: object, mock_patron_repository: object) -> None:
        mock_patron_repository.get_by_id.return_value = None

        result = service.can_borrow_copies('p1')

        assert result is False

    def test_can_borrow_copies_when_patron_not_active(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.SUSPENDED.value
        mock_patron_repository.get_by_id.return_value = mock_patron
        mock_loan_repository.find_by_patron_id.return_value = []

        result = service.can_borrow_copies('p1')

        assert result is False

    def test_can_borrow_copies_when_has_existing_loans(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.ACTIVE.value
        mock_patron_repository.get_by_id.return_value = mock_patron
        mock_loan_repository.find_by_patron_id.return_value = [Mock(spec=Loan)]

        result = service.can_borrow_copies('p1')

        assert result is False

    def test_can_renew_copy_when_valid(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.ACTIVE.value
        mock_patron_repository.get_by_id.return_value = mock_patron

        mock_loan = Mock(spec=Loan)
        mock_loan.copy_id = 'c1'
        mock_loan_repository.find_by_patron_id.return_value = [mock_loan]

        result = service.can_renew_copy('p1', 'c1')

        assert result is True

    def test_can_renew_copy_when_patron_not_found(self, service: object, mock_patron_repository: object) -> None:
        mock_patron_repository.get_by_id.return_value = None

        result = service.can_renew_copy('p1', 'c1')

        assert result is False

    def test_can_renew_copy_when_loan_not_found(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.ACTIVE.value
        mock_patron_repository.get_by_id.return_value = mock_patron

        mock_loan = Mock(spec=Loan)
        mock_loan.copy_id = 'c2'
        mock_loan_repository.find_by_patron_id.return_value = [mock_loan]

        result = service.can_renew_copy('p1', 'c1')

        assert result is False

    def test_can_renew_copy_when_patron_not_active(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.SUSPENDED.value
        mock_patron_repository.get_by_id.return_value = mock_patron

        mock_loan = Mock(spec=Loan)
        mock_loan.copy_id = 'c1'
        mock_loan_repository.find_by_patron_id.return_value = [mock_loan]

        result = service.can_renew_copy('p1', 'c1')

        assert result is False

    def test_can_renew_copy_when_multiple_loans(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.ACTIVE.value
        mock_patron_repository.get_by_id.return_value = mock_patron

        mock_loan1 = Mock(spec=Loan)
        mock_loan1.copy_id = 'c1'
        mock_loan2 = Mock(spec=Loan)
        mock_loan2.copy_id = 'c2'
        mock_loan_repository.find_by_patron_id.return_value = [mock_loan1, mock_loan2]

        result = service.can_renew_copy('p1', 'c1')

        assert result is False


class TestPatronHoldingService:
    @pytest.fixture
    def mock_hold_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_hold_repository: Iterator) -> Iterator:
        return PatronHoldingService(hold_repository=mock_hold_repository)

    def test_can_place_holds_when_no_holds(self, service: object, mock_hold_repository: object) -> None:
        mock_hold_repository.find_active_holds_by_patron.return_value = []

        result = service.can_place_holds('p1')

        assert result is True
        mock_hold_repository.find_active_holds_by_patron.assert_called_once_with(patron_id='p1')

    def test_can_place_holds_when_one_hold(self, service: object, mock_hold_repository: object) -> None:
        mock_hold_repository.find_active_holds_by_patron.return_value = [Mock(spec=Hold)]

        result = service.can_place_holds('p1')

        assert result is True

    def test_can_place_holds_when_two_holds(self, service: object, mock_hold_repository: object) -> None:
        mock_hold_repository.find_active_holds_by_patron.return_value = [Mock(spec=Hold), Mock(spec=Hold)]

        result = service.can_place_holds('p1')

        assert result is False


class TestPatronReinstatementService:
    @pytest.fixture
    def mock_patron_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def mock_loan_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_patron_repository: Iterator, mock_loan_repository: Iterator) -> Iterator:
        return PatronReinstatementService(
            patron_repository=mock_patron_repository, loan_repository=mock_loan_repository
        )

    def test_can_reinstate_when_suspended_and_no_loans(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.SUSPENDED.value
        mock_patron_repository.get_by_id.return_value = mock_patron
        mock_loan_repository.find_by_patron_id.return_value = []

        result = service.can_reinstate('p1')

        assert result is True

    def test_can_reinstate_when_patron_not_found(self, service: object, mock_patron_repository: object) -> None:
        mock_patron_repository.get_by_id.return_value = None

        result = service.can_reinstate('p1')

        assert result is False

    def test_can_reinstate_when_patron_not_suspended(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.ACTIVE.value
        mock_patron_repository.get_by_id.return_value = mock_patron
        mock_loan_repository.find_by_patron_id.return_value = []

        result = service.can_reinstate('p1')

        assert result is False

    def test_can_reinstate_when_has_loans(
        self, service: object, mock_patron_repository: object, mock_loan_repository: object
    ) -> None:
        mock_patron = Mock(spec=Patron)
        mock_patron.status = PatronStatus.SUSPENDED.value
        mock_patron_repository.get_by_id.return_value = mock_patron
        mock_loan_repository.find_by_patron_id.return_value = [Mock(spec=Loan)]

        result = service.can_reinstate('p1')

        assert result is False


class TestFinePolicyService:
    @pytest.fixture
    def mock_copy_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def mock_item_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_copy_repository: Iterator, mock_item_repository: Iterator) -> Iterator:
        return FinePolicyService(copy_repository=mock_copy_repository, item_repository=mock_item_repository)

    def test_calculate_overdue_fine(self, service: object) -> None:
        days_late = 10

        fine = service.calculate_overdue_fine(days_late)

        assert fine == Decimal('5.0')  # 10 * 0.5

    def test_calculate_overdue_fine_one_day(self, service: object) -> None:
        days_late = 1

        fine = service.calculate_overdue_fine(days_late)

        assert fine == Decimal('0.5')

    def test_calculate_fine_for_damaged_book(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.BOOK.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_damaged_item('c1')

        assert fine == Decimal('30.0')  # 20.0 damage + 10.0 processing

    def test_calculate_fine_for_damaged_dvd(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.DVD.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_damaged_item('c1')

        assert fine == Decimal('35.0')  # 25.0 damage + 10.0 processing

    def test_calculate_fine_for_damaged_cd(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.CD.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_damaged_item('c1')

        assert fine == Decimal('25.0')  # 15.0 damage + 10.0 processing

    def test_calculate_fine_for_damaged_magazine(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.MAGAZINE.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_damaged_item('c1')

        assert fine == Decimal('25.0')  # 15.0 damage + 10.0 processing

    def test_calculate_fine_for_damaged_ebook(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.EBOOK.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_damaged_item('c1')

        assert fine == Decimal('11.0')  # 1.0 damage + 10.0 processing

    def test_calculate_fine_for_damaged_item_copy_not_found(
        self, service: object, mock_copy_repository: object
    ) -> None:
        mock_copy_repository.get_by_id.return_value = None

        with pytest.raises(DomainNotFound) as exc_info:
            service.calculate_fine_for_damaged_item('c1')

        assert exc_info.value.domain_name == 'Copy'
        assert exc_info.value.domain_id == 'c1'

    def test_calculate_fine_for_damaged_item_item_not_found(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy
        mock_item_repository.get_by_id.return_value = None

        with pytest.raises(DomainNotFound) as exc_info:
            service.calculate_fine_for_damaged_item('c1')

        assert exc_info.value.domain_name == 'Item'
        assert exc_info.value.domain_id == 'item1'

    def test_calculate_fine_for_lost_book(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.BOOK.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_lost_item('c1')

        assert fine == Decimal('60.0')  # 50.0 replacement + 10.0 processing

    def test_calculate_fine_for_lost_dvd(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.DVD.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_lost_item('c1')

        assert fine == Decimal('45.0')  # 35.0 replacement + 10.0 processing

    def test_calculate_fine_for_lost_cd(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.CD.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_lost_item('c1')

        assert fine == Decimal('45.0')  # 35.0 replacement + 10.0 processing

    def test_calculate_fine_for_lost_magazine(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.MAGAZINE.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_lost_item('c1')

        assert fine == Decimal('35.0')  # 25.0 replacement + 10.0 processing

    def test_calculate_fine_for_lost_ebook(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy

        mock_item = Mock(spec=Item)
        mock_item.format = ItemFormat.EBOOK.value
        mock_item_repository.get_by_id.return_value = mock_item

        fine = service.calculate_fine_for_lost_item('c1')

        assert fine == Decimal('25.0')  # 15.0 replacement + 10.0 processing

    def test_calculate_fine_for_lost_item_copy_not_found(self, service: object, mock_copy_repository: object) -> None:
        mock_copy_repository.get_by_id.return_value = None

        with pytest.raises(DomainNotFound) as exc_info:
            service.calculate_fine_for_lost_item('c1')

        assert exc_info.value.domain_name == 'Copy'
        assert exc_info.value.domain_id == 'c1'

    def test_calculate_fine_for_lost_item_item_not_found(
        self, service: object, mock_copy_repository: object, mock_item_repository: object
    ) -> None:
        mock_copy = Mock(spec=Copy)
        mock_copy.item_id = 'item1'
        mock_copy_repository.get_by_id.return_value = mock_copy
        mock_item_repository.get_by_id.return_value = None

        with pytest.raises(DomainNotFound) as exc_info:
            service.calculate_fine_for_lost_item('c1')

        assert exc_info.value.domain_name == 'Item'
        assert exc_info.value.domain_id == 'item1'
