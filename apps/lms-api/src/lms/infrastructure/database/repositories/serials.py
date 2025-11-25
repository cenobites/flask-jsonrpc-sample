from __future__ import annotations

import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.serials.entities import Serial, SerialIssue
from lms.infrastructure.database import RepositoryError
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
        try:
            models = self.session.query(SerialModel).all()
            return [SerialMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve serials', cause=e) from e

    def get_by_id(self, serial_id: str) -> Serial | None:
        try:
            model = self.session.get(SerialModel, serial_id)
            return SerialMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve serial', cause=e) from e

    def save(self, serial: Serial) -> Serial:
        model = self.session.get(SerialModel, serial.id)
        if not model:
            model = SerialMapper.from_entity(serial)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save serial', cause=e) from e
            serial.id = str(model.id)
            return serial
        model.title = serial.title
        model.issn = serial.issn
        model.frequency = SerialFrequency(serial.frequency) if serial.frequency else None
        model.description = serial.description
        model.status = SerialStatus(serial.status)
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to save serial', cause=e) from e
        return serial

    def delete_by_id(self, serial_id: str) -> None:
        try:
            self.session.query(SerialModel).filter_by(id=serial_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete serial', cause=e) from e


class SQLAlchemySerialIssueRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[SerialIssue]:
        try:
            models = self.session.query(SerialIssueModel).all()
            return [SerialIssueMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve serial issues', cause=e) from e

    def get_by_id(self, issue_id: str) -> SerialIssue | None:
        try:
            model = self.session.get(SerialIssueModel, issue_id)
            return SerialIssueMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve serial issue', cause=e) from e

    def save(self, issue: SerialIssue) -> SerialIssue:
        model = self.session.get(SerialIssueModel, issue.id)
        if not model:
            model = SerialIssueMapper.from_entity(issue)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save serial issue', cause=e) from e
            issue.id = str(model.id)
            return issue
        model.issue_number = issue.issue_number
        model.date_received = issue.date_received
        model.status = SerialIssueStatus(issue.status)
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to update serial issue', cause=e) from e
        return issue

    def delete_by_id(self, issue_id: str) -> None:
        try:
            self.session.query(SerialIssueModel).filter_by(id=issue_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete serial issue', cause=e) from e
