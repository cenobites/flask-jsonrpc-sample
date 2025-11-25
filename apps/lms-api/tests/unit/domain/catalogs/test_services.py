from unittest.mock import Mock
from collections.abc import Iterator

import pytest

from lms.domain.catalogs.services import ItemUniquenessService


class TestItemUniquenessService:
    @pytest.fixture
    def mock_item_repository(self) -> Iterator:
        return Mock()

    @pytest.fixture
    def service(self, mock_item_repository: Iterator) -> Iterator:
        return ItemUniquenessService(item_repository=mock_item_repository)

    def test_is_title_unique_when_title_does_not_exist(self, service: object, mock_item_repository: object) -> None:
        mock_item_repository.exists_by_title.return_value = False

        result = service.is_title_unique('New Book Title')

        assert result is True
        mock_item_repository.exists_by_title.assert_called_once_with('New Book Title')

    def test_is_title_unique_when_title_exists(self, service: object, mock_item_repository: object) -> None:
        mock_item_repository.exists_by_title.return_value = True

        result = service.is_title_unique('Existing Book Title')

        assert result is False
        mock_item_repository.exists_by_title.assert_called_once_with('Existing Book Title')
