from datetime import date, timedelta
from unittest.mock import Mock
from collections.abc import Iterator

import pytest

from lms.domain.patrons.entities import Patron
from lms.domain.catalogs.entities import Copy
from lms.domain.circulations.services import HoldPolicyService, LoanPolicyService


class TestLoanPolicyService:
    @pytest.fixture
    def service(self) -> Iterator:
        return LoanPolicyService()

    @pytest.fixture
    def mock_patron(self) -> Iterator:
        patron = Mock(spec=Patron)
        patron.is_premium_membership.return_value = False
        return patron

    @pytest.fixture
    def mock_copy(self) -> Iterator:
        copy = Mock(spec=Copy)
        copy.is_older_version.return_value = False
        return copy

    def test_calculate_due_date_for_regular_patron_and_new_copy(
        self, service: object, mock_patron: object, mock_copy: object
    ) -> None:
        loan_date = date(2025, 1, 1)

        due_date = service.calculate_due_date(loan_date, mock_patron, mock_copy)

        assert due_date == date(2025, 1, 15)  # 14 days later

    def test_calculate_due_date_for_premium_patron(
        self, service: object, mock_patron: object, mock_copy: object
    ) -> None:
        mock_patron.is_premium_membership.return_value = True
        loan_date = date(2025, 1, 1)

        due_date = service.calculate_due_date(loan_date, mock_patron, mock_copy)

        assert due_date == date(2025, 1, 29)  # 28 days later

    def test_calculate_due_date_for_older_copy(self, service: object, mock_patron: object, mock_copy: object) -> None:
        mock_copy.is_older_version.return_value = True
        loan_date = date(2025, 1, 1)

        due_date = service.calculate_due_date(loan_date, mock_patron, mock_copy)

        assert due_date == date(2025, 1, 29)  # 28 days later

    def test_calculate_due_date_for_premium_patron_and_older_copy(
        self, service: object, mock_patron: object, mock_copy: object
    ) -> None:
        mock_patron.is_premium_membership.return_value = True
        mock_copy.is_older_version.return_value = True
        loan_date = date(2025, 1, 1)

        due_date = service.calculate_due_date(loan_date, mock_patron, mock_copy)

        assert due_date == date(2025, 1, 29)  # 28 days later

    def test_calculate_new_due_date(self, service: object, mock_patron: object, mock_copy: object) -> None:
        expected_due_date = date.today() + timedelta(days=14)

        due_date = service.calculate_new_due_date(mock_patron, mock_copy)

        assert due_date == expected_due_date


class TestHoldPolicyService:
    @pytest.fixture
    def mock_hold_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self: Iterator, mock_hold_repository: Iterator) -> Iterator:
        return HoldPolicyService(hold_repository=mock_hold_repository)

    def test_calculate_hold_expiry_date(self, service: object) -> None:
        request_date = date(2025, 1, 1)

        expiry_date = service.calculate_hold_expiry_date(request_date)

        assert expiry_date == date(2025, 1, 8)  # 7 days later

    def test_is_hold_expired_when_not_expired(self, service: object) -> None:
        request_date = date.today()

        result = service.is_hold_expired(request_date)

        assert result is False

    def test_is_hold_expired_when_expired(self, service: object) -> None:
        request_date = date.today() - timedelta(days=10)

        result = service.is_hold_expired(request_date)

        assert result is True

    def test_is_hold_expired_on_expiry_date(self, service: object) -> None:
        request_date = date.today() - timedelta(days=7)

        result = service.is_hold_expired(request_date)

        assert result is False  # On expiry date, not yet expired
