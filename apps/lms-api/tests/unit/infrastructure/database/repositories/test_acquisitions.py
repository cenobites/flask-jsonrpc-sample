"""Unit tests for acquisitions repositories - function-based with 100% coverage."""

from unittest.mock import Mock, patch

import pytest
import sqlalchemy.exc as sa_exc

from tests.unit.factories import VendorFactory, AcquisitionOrderFactory
from lms.infrastructure.database import RepositoryError
from lms.infrastructure.database.repositories.acquisitions import (
    SQLAlchemyVendorRepository,
    SQLAlchemyAcquisitionOrderRepository,
    SQLAlchemyAcquisitionOrderLineRepository,
)


# Fixtures
@pytest.fixture
def mock_session() -> Mock:
    return Mock()


# SQLAlchemyAcquisitionOrderRepository Tests
def test_acquisition_order_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)
    mock_order1 = AcquisitionOrderFactory.build()
    mock_order2 = AcquisitionOrderFactory.build()
    mock_session.query.return_value.all.return_value = [mock_order1, mock_order2]

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        orders = repo.find_all()

        assert len(orders) == 2
        assert mock_mapper.to_entity.call_count == 2


def test_acquisition_order_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve acquisition orders'):
        repo.find_all()


def test_acquisition_order_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)
    mock_order = AcquisitionOrderFactory.build()
    mock_session.get.return_value = mock_order

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_order
        order = repo.get_by_id('order1')

        assert order == mock_order


def test_acquisition_order_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)
    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderMapper'):
        order = repo.get_by_id('order1')

        assert order is None


def test_acquisition_order_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve acquisition order'):
        repo.get_by_id('order1')


def test_acquisition_order_save_new_order(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)
    mock_order = Mock()
    mock_order.id = None
    mock_model = AcquisitionOrderFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        result = repo.save(mock_order)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert result == mock_order


def test_acquisition_order_save_new_order_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)
    mock_order = Mock()
    mock_order.id = None
    mock_model = AcquisitionOrderFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save acquisition order'):
            repo.save(mock_order)

        mock_session.rollback.assert_called_once()


def test_acquisition_order_save_existing_order(mock_session: Mock) -> None:
    from datetime import date

    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)

    mock_order = Mock()
    mock_order.id = 'order1'
    mock_order.received_date = date(2024, 1, 15)
    mock_order.status = 'received'

    # Create mock lines to test line deletion and ID assignment
    mock_order_line = Mock()
    mock_order_line.id = None
    mock_order.order_lines = [mock_order_line]

    mock_model = Mock()
    mock_old_line = Mock()
    mock_model.order_lines = [mock_old_line]

    mock_new_line_model = Mock()
    mock_new_line_model.id = 'line123'

    mock_session.get.return_value = mock_model

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderLineMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_new_line_model
        result = repo.save(mock_order)

        assert mock_model.received_date == date(2024, 1, 15)
        mock_session.delete.assert_called_once_with(mock_old_line)
        mock_session.commit.assert_called_once()
        assert mock_order_line.id == 'line123'
        assert result == mock_order


def test_acquisition_order_save_existing_order_rollback_on_error(mock_session: Mock) -> None:
    from datetime import date

    repo = SQLAlchemyAcquisitionOrderRepository(session=mock_session)

    mock_order = Mock()
    mock_order.id = 'order1'
    mock_order.received_date = date(2024, 1, 15)
    mock_order.status = 'received'
    mock_order.order_lines = []

    mock_model = Mock()
    mock_model.order_lines = []

    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderLineMapper'):
        with pytest.raises(RepositoryError, match='Failed to update acquisition order'):
            repo.save(mock_order)

        mock_session.rollback.assert_called_once()


# SQLAlchemyAcquisitionOrderLineRepository Tests
def test_acquisition_order_line_find_by_order(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderLineRepository(session=mock_session)
    mock_line1 = Mock()
    mock_line2 = Mock()
    mock_session.query.return_value.filter_by.return_value.all.return_value = [mock_line1, mock_line2]

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderLineMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        lines = repo.find_by_order('order1')

        assert len(lines) == 2


def test_acquisition_order_line_find_by_order_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderLineRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve acquisition order lines'):
        repo.find_by_order('order1')


def test_acquisition_order_line_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderLineRepository(session=mock_session)
    mock_line = Mock()
    mock_session.get.return_value = mock_line

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderLineMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_line
        line = repo.get_by_id('line1')

        assert line == mock_line


def test_acquisition_order_line_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderLineRepository(session=mock_session)
    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.acquisitions.AcquisitionOrderLineMapper'):
        line = repo.get_by_id('line1')

        assert line is None


def test_acquisition_order_line_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyAcquisitionOrderLineRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve acquisition order line'):
        repo.get_by_id('line1')


# SQLAlchemyVendorRepository Tests
def test_vendor_find_all(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_vendor1 = VendorFactory.build()
    mock_vendor2 = VendorFactory.build()
    mock_session.query.return_value.all.return_value = [mock_vendor1, mock_vendor2]

    with patch('lms.infrastructure.database.repositories.acquisitions.VendorMapper') as mock_mapper:
        mock_mapper.to_entity.side_effect = lambda m: m
        vendors = repo.find_all()

        assert len(vendors) == 2


def test_vendor_find_all_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_session.query.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve vendors'):
        repo.find_all()


def test_vendor_get_by_id(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_vendor = VendorFactory.build()
    mock_session.get.return_value = mock_vendor

    with patch('lms.infrastructure.database.repositories.acquisitions.VendorMapper') as mock_mapper:
        mock_mapper.to_entity.return_value = mock_vendor
        vendor = repo.get_by_id('vendor1')

        assert vendor == mock_vendor


def test_vendor_get_by_id_returns_none_when_not_found(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.acquisitions.VendorMapper'):
        vendor = repo.get_by_id('vendor1')

        assert vendor is None


def test_vendor_get_by_id_raises_repository_error_on_db_error(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_session.get.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to retrieve vendor'):
        repo.get_by_id('vendor1')


def test_vendor_save_new_vendor(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_vendor = Mock()
    mock_vendor.id = None
    mock_model = VendorFactory.build()

    mock_session.get.return_value = None

    with patch('lms.infrastructure.database.repositories.acquisitions.VendorMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model
        result = repo.save(mock_vendor)

        mock_session.add.assert_called_once_with(mock_model)
        mock_session.commit.assert_called_once()
        assert result == mock_vendor


def test_vendor_save_new_vendor_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_vendor = Mock()
    mock_vendor.id = None
    mock_model = VendorFactory.build()

    mock_session.get.return_value = None
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with patch('lms.infrastructure.database.repositories.acquisitions.VendorMapper') as mock_mapper:
        mock_mapper.from_entity.return_value = mock_model

        with pytest.raises(RepositoryError, match='Failed to save vendor'):
            repo.save(mock_vendor)

        mock_session.rollback.assert_called_once()


def test_vendor_save_existing_vendor(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_vendor = Mock()
    mock_vendor.id = 'vendor1'
    mock_vendor.name = 'Updated Vendor'
    mock_vendor.address = 'New Address'
    mock_vendor.email = 'new@vendor.com'
    mock_vendor.phone = '555-0123'

    mock_model = Mock()
    mock_session.get.return_value = mock_model

    result = repo.save(mock_vendor)

    assert mock_model.name == 'Updated Vendor'
    assert mock_model.address == 'New Address'
    assert mock_model.email == 'new@vendor.com'
    assert mock_model.phone == '555-0123'
    mock_session.commit.assert_called_once()
    assert result == mock_vendor


def test_vendor_save_existing_vendor_rollback_on_error(mock_session: Mock) -> None:
    repo = SQLAlchemyVendorRepository(session=mock_session)
    mock_vendor = Mock()
    mock_vendor.id = 'vendor1'
    mock_vendor.name = 'Updated Vendor'
    mock_vendor.address = 'New Address'
    mock_vendor.email = 'new@vendor.com'
    mock_vendor.phone = '555-0123'

    mock_model = Mock()
    mock_session.get.return_value = mock_model
    mock_session.commit.side_effect = sa_exc.SQLAlchemyError('DB Error')

    with pytest.raises(RepositoryError, match='Failed to update vendor'):
        repo.save(mock_vendor)

    mock_session.rollback.assert_called_once()
