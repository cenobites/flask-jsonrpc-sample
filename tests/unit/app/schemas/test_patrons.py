from __future__ import annotations

import pytest
from pydantic import ValidationError

from lms.app.schemas.patrons import PatronCreate, PatronUpdate


def test_patron_create_all_fields() -> None:
    patron = PatronCreate(branch_id='branch-123', name='Jane Smith', email='jane.smith@example.com')

    assert patron.branch_id == 'branch-123'
    assert patron.name == 'Jane Smith'
    assert patron.email == 'jane.smith@example.com'


def test_patron_create_requires_all_fields() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PatronCreate(branch_id='branch-123', name='Jane Smith')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('email',) for error in errors)


def test_patron_create_name_min_length() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PatronCreate(branch_id='branch-123', name='', email='test@example.com')

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_patron_create_name_max_length() -> None:
    long_name = 'A' * 301

    with pytest.raises(ValidationError) as exc_info:
        PatronCreate(branch_id='branch-123', name=long_name, email='test@example.com')

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_patron_create_email_validation() -> None:
    invalid_emails = ['invalid', 'test@', '@example.com', 'test @example.com', 'test@.com']

    for invalid_email in invalid_emails:
        with pytest.raises(ValidationError) as exc_info:
            PatronCreate(branch_id='branch-123', name='Test Patron', email=invalid_email)

        errors = exc_info.value.errors()
        assert any('email' in str(error['loc']) for error in errors)


def test_patron_create_valid_emails() -> None:
    valid_emails = ['test@example.com', 'user.name@example.com', 'user+tag@example.co.uk', 'test123@test-domain.com']

    for valid_email in valid_emails:
        patron = PatronCreate(branch_id='branch-123', name='Test Patron', email=valid_email)
        assert patron.email == valid_email


def test_patron_create_strips_whitespace() -> None:
    patron = PatronCreate(branch_id='branch-123', name='  John Doe  ', email='john@example.com')

    assert patron.name == 'John Doe'


def test_patron_create_different_branch_ids() -> None:
    branch_ids = ['branch-1', 'branch-abc', 'branch-999', 'main-branch']

    for branch_id in branch_ids:
        patron = PatronCreate(branch_id=branch_id, name='Test Patron', email='test@example.com')
        assert patron.branch_id == branch_id


def test_patron_update_requires_id_and_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PatronUpdate(id='patron-123')  # type: ignore

    errors = exc_info.value.errors()
    assert any(error['loc'] == ('name',) for error in errors)


def test_patron_update_all_fields() -> None:
    patron = PatronUpdate(id='patron-123', name='Updated Name')

    assert patron.id == 'patron-123'
    assert patron.name == 'Updated Name'


def test_patron_update_name_min_length() -> None:
    with pytest.raises(ValidationError) as exc_info:
        PatronUpdate(id='patron-123', name='')

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_patron_update_name_max_length() -> None:
    long_name = 'A' * 301

    with pytest.raises(ValidationError) as exc_info:
        PatronUpdate(id='patron-123', name=long_name)

    errors = exc_info.value.errors()
    assert any('name' in str(error['loc']) for error in errors)


def test_patron_update_strips_whitespace() -> None:
    patron = PatronUpdate(id='patron-123', name='  Jane Doe  ')

    assert patron.name == 'Jane Doe'


def test_patron_create_serialization() -> None:
    patron = PatronCreate(branch_id='branch-1', name='John Doe', email='john@example.com')
    data = patron.model_dump()

    assert data == {'branch_id': 'branch-1', 'name': 'John Doe', 'email': 'john@example.com'}


def test_patron_update_serialization() -> None:
    patron = PatronUpdate(id='patron-1', name='Jane Doe')
    data = patron.model_dump()

    assert data == {'id': 'patron-1', 'name': 'Jane Doe'}


def test_patron_create_name_boundary_values() -> None:
    # Minimum valid length (1 character)
    patron1 = PatronCreate(branch_id='branch-1', name='A', email='test@example.com')
    assert patron1.name == 'A'

    # Maximum valid length (300 characters)
    max_name = 'A' * 300
    patron2 = PatronCreate(branch_id='branch-1', name=max_name, email='test@example.com')
    assert patron2.name == max_name


def test_patron_update_name_boundary_values() -> None:
    # Minimum valid length (1 character)
    patron1 = PatronUpdate(id='patron-1', name='A')
    assert patron1.name == 'A'

    # Maximum valid length (300 characters)
    max_name = 'A' * 300
    patron2 = PatronUpdate(id='patron-1', name=max_name)
    assert patron2.name == max_name


def test_patron_create_special_characters_in_name() -> None:
    special_names = ["O'Brien", 'Jean-Paul', 'María García', 'José Silva', 'François Müller']

    for name in special_names:
        patron = PatronCreate(branch_id='branch-1', name=name, email='test@example.com')
        assert patron.name == name
