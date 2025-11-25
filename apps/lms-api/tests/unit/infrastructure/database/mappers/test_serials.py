"""Unit tests for serials mappers - function-based with comprehensive coverage."""

import uuid
from datetime import date

from lms.domain.serials.entities import Serial, SerialIssue
from lms.infrastructure.database.models.serials import (
    SerialModel,
    SerialStatus,
    SerialFrequency,
    SerialIssueModel,
    SerialIssueStatus,
)
from lms.infrastructure.database.mappers.serials import SerialMapper, SerialIssueMapper


# SerialMapper Tests
def test_serial_mapper_to_entity_with_all_fields() -> None:
    model = SerialModel()
    model.id = uuid.uuid4()
    model.title = 'Science Monthly'
    model.issn = '1234-5678'
    model.item_id = uuid.uuid4()
    model.frequency = SerialFrequency.MONTHLY
    model.description = 'A monthly science journal'
    model.status = SerialStatus.ACTIVE

    entity = SerialMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.title == 'Science Monthly'
    assert entity.issn == '1234-5678'
    assert entity.item_id == str(model.item_id)
    assert entity.frequency == 'monthly'
    assert entity.description == 'A monthly science journal'
    assert entity.status == 'active'


def test_serial_mapper_to_entity_with_optional_fields_none() -> None:
    model = SerialModel()
    model.id = uuid.uuid4()
    model.title = 'Tech Weekly'
    model.issn = '8765-4321'
    model.item_id = uuid.uuid4()
    model.frequency = None
    model.description = None
    model.status = SerialStatus.INACTIVE

    entity = SerialMapper.to_entity(model)

    assert entity.frequency is None
    assert entity.description is None
    assert entity.status == 'inactive'


def test_serial_mapper_to_entity_without_id() -> None:
    model = SerialModel()
    model.id = None
    model.title = 'Weekly News'
    model.issn = '1111-2222'
    model.item_id = uuid.uuid4()
    model.frequency = SerialFrequency.WEEKLY
    model.description = 'Weekly publication'
    model.status = SerialStatus.ACTIVE

    entity = SerialMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.frequency == 'weekly'


def test_serial_mapper_from_entity_with_all_fields() -> None:
    entity = Serial(
        id=str(uuid.uuid4()),
        title='Science Monthly',
        issn='1234-5678',
        item_id=str(uuid.uuid4()),
        frequency='monthly',
        description='A monthly science journal',
        status='active',
    )

    model = SerialMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert model.title == 'Science Monthly'
    assert model.issn == '1234-5678'
    assert str(model.item_id) == entity.item_id
    assert model.frequency == SerialFrequency.MONTHLY
    assert model.description == 'A monthly science journal'
    assert model.status == SerialStatus.ACTIVE


def test_serial_mapper_from_entity_with_optional_fields_none() -> None:
    entity = Serial(
        id=str(uuid.uuid4()),
        title='Quarterly Review',
        issn='3333-4444',
        item_id=str(uuid.uuid4()),
        frequency=None,
        description=None,
        status='inactive',
    )

    model = SerialMapper.from_entity(entity)

    assert model.frequency is None
    assert model.description is None
    assert model.status == SerialStatus.INACTIVE


def test_serial_mapper_from_entity_without_id() -> None:
    entity = Serial(
        id=None,
        title='Yearly Report',
        issn='5555-6666',
        item_id=str(uuid.uuid4()),
        frequency='yearly',
        description='Annual publication',
        status='active',
    )

    model = SerialMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.frequency == SerialFrequency.YEARLY


# SerialIssueMapper Tests
def test_serial_issue_mapper_to_entity_with_all_fields() -> None:
    model = SerialIssueModel()
    model.id = uuid.uuid4()
    model.serial_id = uuid.uuid4()
    model.issue_number = '2024-03'
    model.date_received = date(2024, 3, 5)
    model.status = SerialIssueStatus.RECEIVED

    entity = SerialIssueMapper.to_entity(model)

    assert entity.id == str(model.id)
    assert entity.serial_id == str(model.serial_id)
    assert entity.issue_number == '2024-03'
    assert entity.date_received == date(2024, 3, 5)
    assert entity.status == 'received'


def test_serial_issue_mapper_to_entity_with_different_status() -> None:
    model = SerialIssueModel()
    model.id = uuid.uuid4()
    model.serial_id = uuid.uuid4()
    model.issue_number = '2024-02'
    model.date_received = date(2024, 2, 3)
    model.status = SerialIssueStatus.MISSING

    entity = SerialIssueMapper.to_entity(model)

    assert entity.status == 'missing'


def test_serial_issue_mapper_to_entity_without_id() -> None:
    model = SerialIssueModel()
    model.id = None
    model.serial_id = uuid.uuid4()
    model.issue_number = '2024-01'
    model.date_received = date(2024, 1, 10)
    model.status = SerialIssueStatus.RECEIVED

    entity = SerialIssueMapper.to_entity(model)

    assert entity.id is not None  # Entity auto-generates ID
    assert entity.status == 'received'


def test_serial_issue_mapper_from_entity_with_all_fields() -> None:
    entity = SerialIssue(
        id=str(uuid.uuid4()),
        serial_id=str(uuid.uuid4()),
        issue_number='2024-03',
        date_received=date(2024, 3, 5),
        status='received',
    )

    model = SerialIssueMapper.from_entity(entity)

    assert str(model.id) == entity.id
    assert str(model.serial_id) == entity.serial_id
    assert model.issue_number == '2024-03'
    assert model.date_received == date(2024, 3, 5)
    assert model.status == SerialIssueStatus.RECEIVED


def test_serial_issue_mapper_from_entity_with_different_status() -> None:
    entity = SerialIssue(
        id=str(uuid.uuid4()),
        serial_id=str(uuid.uuid4()),
        issue_number='2024-04',
        date_received=date(2024, 4, 8),
        status='lost',
    )

    model = SerialIssueMapper.from_entity(entity)

    assert model.status == SerialIssueStatus.LOST


def test_serial_issue_mapper_from_entity_without_id() -> None:
    entity = SerialIssue(
        id=None, serial_id=str(uuid.uuid4()), issue_number='2024-01', date_received=date(2024, 1, 10), status='received'
    )

    model = SerialIssueMapper.from_entity(entity)

    assert model.id is not None  # Model gets auto-generated ID from entity
    assert model.status == SerialIssueStatus.RECEIVED
