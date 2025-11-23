from __future__ import annotations

import pytest
from pydantic import ValidationError

from lms.app.schemas.serials import SerialCreate


def test_serial_create_all_fields() -> None:
    serial = SerialCreate(
        title='Nature Magazine',
        issn='0028-0836',
        item_id='item-123',
        frequency='Monthly',
        description='International scientific journal',
    )

    assert serial.title == 'Nature Magazine'
    assert serial.issn == '0028-0836'
    assert serial.item_id == 'item-123'
    assert serial.frequency == 'Monthly'
    assert serial.description == 'International scientific journal'


def test_serial_create_without_optional_fields() -> None:
    serial = SerialCreate(title='Science Journal', issn='1234-5678', item_id='item-456')

    assert serial.title == 'Science Journal'
    assert serial.issn == '1234-5678'
    assert serial.item_id == 'item-456'
    assert serial.frequency is None
    assert serial.description is None


def test_serial_create_requires_title() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(issn='1234-5678', item_id='item-123')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('title',) for error in errors)


def test_serial_create_requires_issn() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(title='Test Serial', item_id='item-123')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('issn',) for error in errors)


def test_serial_create_requires_item_id() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(title='Test Serial', issn='1234-5678')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('item_id',) for error in errors)


def test_serial_create_title_min_length() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(title='', issn='1234-5678', item_id='item-123')

    errors = exc_info.value.errors()
    assert any('title' in str(error['loc']) for error in errors)


def test_serial_create_title_max_length() -> None:
    long_title = 'A' * 256

    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(title=long_title, issn='1234-5678', item_id='item-123')

    errors = exc_info.value.errors()
    assert any('title' in str(error['loc']) for error in errors)


def test_serial_create_issn_min_length() -> None:
    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(title='Test Serial', issn='', item_id='item-123')

    errors = exc_info.value.errors()
    assert any('issn' in str(error['loc']) for error in errors)


def test_serial_create_issn_max_length() -> None:
    long_issn = '1' * 31

    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(title='Test Serial', issn=long_issn, item_id='item-123')

    errors = exc_info.value.errors()
    assert any('issn' in str(error['loc']) for error in errors)


def test_serial_create_frequency_max_length() -> None:
    long_frequency = 'A' * 51

    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(title='Test Serial', issn='1234-5678', item_id='item-123', frequency=long_frequency)

    errors = exc_info.value.errors()
    assert any('frequency' in str(error['loc']) for error in errors)


def test_serial_create_description_max_length() -> None:
    long_description = 'A' * 1001

    with pytest.raises(ValidationError) as exc_info:
        SerialCreate(title='Test Serial', issn='1234-5678', item_id='item-123', description=long_description)

    errors = exc_info.value.errors()
    assert any('description' in str(error['loc']) for error in errors)


def test_serial_create_various_frequencies() -> None:
    frequencies = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Annually', 'Biweekly']

    for freq in frequencies:
        serial = SerialCreate(title='Test Serial', issn='1234-5678', item_id='item-123', frequency=freq)
        assert serial.frequency == freq


def test_serial_create_strips_whitespace() -> None:
    serial = SerialCreate(
        title='  Test Serial  ', issn='  1234-5678  ', item_id='  item-123  ', frequency='  Monthly  '
    )

    assert serial.title == 'Test Serial'
    assert serial.issn == '1234-5678'
    assert serial.item_id == 'item-123'
    assert serial.frequency == 'Monthly'


def test_serial_create_issn_formats() -> None:
    issn_formats = ['0028-0836', '1234-5678', '2049-3630', '1932-6203']

    for issn in issn_formats:
        serial = SerialCreate(title='Test Serial', issn=issn, item_id='item-123')
        assert serial.issn == issn


def test_serial_create_serialization() -> None:
    serial = SerialCreate(
        title='Test Serial', issn='1234-5678', item_id='item-123', frequency='Monthly', description='Test description'
    )
    data = serial.model_dump()

    assert data == {
        'title': 'Test Serial',
        'issn': '1234-5678',
        'item_id': 'item-123',
        'frequency': 'Monthly',
        'description': 'Test description',
    }


def test_serial_create_boundary_title_length() -> None:
    # Minimum valid length (1 character)
    serial1 = SerialCreate(title='A', issn='1234-5678', item_id='item-123')
    assert serial1.title == 'A'

    # Maximum valid length (255 characters)
    max_title = 'A' * 255
    serial2 = SerialCreate(title=max_title, issn='1234-5678', item_id='item-123')
    assert serial2.title == max_title


def test_serial_create_boundary_issn_length() -> None:
    # Minimum valid length (1 character)
    serial1 = SerialCreate(title='Test', issn='1', item_id='item-123')
    assert serial1.issn == '1'

    # Maximum valid length (30 characters)
    max_issn = '1' * 30
    serial2 = SerialCreate(title='Test', issn=max_issn, item_id='item-123')
    assert serial2.issn == max_issn


def test_serial_create_boundary_frequency_length() -> None:
    # Maximum valid length (50 characters)
    max_frequency = 'A' * 50
    serial = SerialCreate(title='Test', issn='1234-5678', item_id='item-123', frequency=max_frequency)
    assert serial.frequency == max_frequency


def test_serial_create_boundary_description_length() -> None:
    # Maximum valid length (1000 characters)
    max_description = 'A' * 1000
    serial = SerialCreate(title='Test', issn='1234-5678', item_id='item-123', description=max_description)
    assert serial.description == max_description
