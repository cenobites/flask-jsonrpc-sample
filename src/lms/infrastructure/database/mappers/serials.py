from __future__ import annotations

import uuid

from lms.domain.serials.entities import Serial, SerialIssue
from lms.infrastructure.database.models.serials import (
    SerialModel,
    SerialStatus,
    SerialFrequency,
    SerialIssueModel,
    SerialIssueStatus,
)


class SerialMapper:
    @staticmethod
    def to_entity(model: SerialModel) -> Serial:
        return Serial(
            id=str(model.id) if model.id else None,
            title=model.title,
            issn=model.issn,
            item_id=str(model.item_id),
            frequency=model.frequency.value if model.frequency else None,
            description=model.description,
            status=model.status.value,
        )

    @staticmethod
    def from_entity(entity: Serial) -> SerialModel:
        model = SerialModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.title = entity.title
        model.issn = entity.issn
        model.item_id = uuid.UUID(entity.item_id)
        model.frequency = SerialFrequency(entity.frequency) if entity.frequency else None
        model.description = entity.description
        model.status = SerialStatus(entity.status)
        return model


class SerialIssueMapper:
    @staticmethod
    def to_entity(model: SerialIssueModel) -> SerialIssue:
        return SerialIssue(
            id=str(model.id) if model.id else None,
            serial_id=str(model.serial_id),
            issue_number=model.issue_number,
            date_received=model.date_received,
            status=model.status.value,
        )

    @staticmethod
    def from_entity(entity: SerialIssue) -> SerialIssueModel:
        model = SerialIssueModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.serial_id = uuid.UUID(entity.serial_id)
        model.issue_number = entity.issue_number
        model.date_received = entity.date_received
        model.status = SerialIssueStatus(entity.status)
        return model
