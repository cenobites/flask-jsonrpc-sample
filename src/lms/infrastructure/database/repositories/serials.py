from __future__ import annotations

import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.serials.entities import Serial, SerialIssue
from lms.infrastructure.database.models.serials import SerialModel, SerialIssueModel


class SQLAlchemySerialRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Serial]:
        models = self.session.query(SerialModel).all()
        return [
            Serial(
                id=m.id,
                title=m.title,
                issn=m.issn,
                publisher_id=m.publisher_id,
                frequency=m.frequency.value if m.frequency else None,
                category_id=m.category_id,
                description=m.description,
            )
            for m in models
        ]

    def get_by_id(self, serial_id: str) -> Serial | None:
        model = self.session.get(SerialModel, serial_id)
        if not model:
            return None
        return Serial(
            id=str(model.id) if model.id else None,
            title=model.title,
            issn=model.issn,
            publisher_id=model.publisher_id,
            frequency=model.frequency.value if model.frequency else None,
            category_id=model.category_id,
            description=model.description,
        )

    def save(self, serial: Serial) -> Serial:
        model = self.session.get(SerialModel, serial.id)
        if not model:
            model = SerialModel(**serial.__dict__)
            self.session.add(model)
            self.session.commit()
            serial.id = str(model.id)
            return serial
        for k, v in serial.__dict__.items():
            setattr(model, k, v)
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
        return [
            SerialIssue(
                id=m.id,
                serial_id=m.serial_id,
                issue_number=m.issue_number,
                date_received=m.date_received,
                status=m.status.value,
            )
            for m in models
        ]

    def get_by_id(self, issue_id: str) -> SerialIssue | None:
        model = self.session.get(SerialIssueModel, issue_id)
        if not model:
            return None
        return SerialIssue(
            id=str(model.id) if model.id else None,
            serial_id=model.serial_id,
            issue_number=model.issue_number,
            date_received=model.date_received,
            status=model.status.value,
        )

    def save(self, issue: SerialIssue) -> SerialIssue:
        model = self.session.get(SerialIssueModel, issue.id)
        if not model:
            model = SerialIssueModel(**issue.__dict__)
            self.session.add(model)
            self.session.commit()
            issue.id = str(model.id)
            return issue
        for k, v in issue.__dict__.items():
            setattr(model, k, v)
        self.session.commit()
        return issue

    def delete_by_id(self, issue_id: str) -> None:
        model = self.session.get(SerialIssueModel, issue_id)
        if model:
            self.session.delete(model)
            self.session.commit()
