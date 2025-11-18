from __future__ import annotations

import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.serials.entities import Serial, SerialIssue
from lms.infrastructure.database.models.serials import (
    SerialModel,
    SerialStatus,
    SerialFrequency,
    SerialIssueModel,
    SerialIssueStatus,
)
from lms.infrastructure.database.mappers.serials import SerialMapper, SerialIssueMapper


class SQLAlchemySerialRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Serial]:
        models = self.session.query(SerialModel).all()
        return [SerialMapper.to_entity(m) for m in models]

    def get_by_id(self, serial_id: str) -> Serial | None:
        model = self.session.get(SerialModel, serial_id)
        return SerialMapper.to_entity(model) if model else None

    def save(self, serial: Serial) -> Serial:
        model = self.session.get(SerialModel, serial.id)
        if not model:
            model = SerialMapper.from_entity(serial)
            self.session.add(model)
            self.session.commit()
            serial.id = str(model.id)
            return serial
        model.title = serial.title
        model.issn = serial.issn
        model.frequency = SerialFrequency(serial.frequency) if serial.frequency else None
        model.description = serial.description
        model.status = SerialStatus(serial.status)
        self.session.commit()
        return serial

    def delete_by_id(self, serial_id: str) -> None:
        model = self.session.get(SerialModel, serial_id)
        if model:
            self.session.delete(model)
            self.session.commit()


class SQLAlchemySerialIssueRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[SerialIssue]:
        models = self.session.query(SerialIssueModel).all()
        return [SerialIssueMapper.to_entity(m) for m in models]

    def get_by_id(self, issue_id: str) -> SerialIssue | None:
        model = self.session.get(SerialIssueModel, issue_id)
        return SerialIssueMapper.to_entity(model) if model else None

    def save(self, issue: SerialIssue) -> SerialIssue:
        model = self.session.get(SerialIssueModel, issue.id)
        if not model:
            model = SerialIssueMapper.from_entity(issue)
            self.session.add(model)
            self.session.commit()
            issue.id = str(model.id)
            return issue
        model.issue_number = issue.issue_number
        model.date_received = issue.date_received
        model.status = SerialIssueStatus(issue.status)
        self.session.commit()
        return issue

    def delete_by_id(self, issue_id: str) -> None:
        model = self.session.get(SerialIssueModel, issue_id)
        if model:
            self.session.delete(model)
            self.session.commit()
