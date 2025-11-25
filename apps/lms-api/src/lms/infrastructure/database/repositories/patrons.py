from __future__ import annotations

import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.patrons.entities import Fine, Patron
from lms.infrastructure.database import RepositoryError
from lms.infrastructure.database.models.patrons import FineModel, FineStatus, PatronModel, PatronStatus
from lms.infrastructure.database.mappers.patrons import FineMapper, PatronMapper


class SQLAlchemyPatronRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Patron]:
        try:
            models = self.session.query(PatronModel).all()
            return [PatronMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve patrons', cause=e) from e

    def get_by_id(self, patron_id: str) -> Patron | None:
        try:
            model = self.session.get(PatronModel, patron_id)
            return PatronMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve patron', cause=e) from e

    def exists_by_email(self, email: str) -> bool:
        try:
            q = self.session.query(PatronModel).filter_by(email=email)
            count = self.session.query(q.exists()).scalar()
            return count is not None and count > 0
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to check patron existence by email', cause=e) from e

    def save(self, patron: Patron) -> Patron:
        model = self.session.get(PatronModel, patron.id)
        if not model:
            model = PatronMapper.from_entity(patron)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save patron', cause=e) from e
            patron.id = str(model.id)
            return patron
        model.name = patron.name
        model.email = patron.email
        model.status = PatronStatus(patron.status)
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to update patron', cause=e) from e
        return patron

    def delete_by_id(self, patron_id: str) -> None:
        try:
            self.session.query(PatronModel).filter_by(id=patron_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete patron', cause=e) from e


class SQLAlchemyFineRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Fine]:
        try:
            models = self.session.query(FineModel).all()
            return [FineMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve fines', cause=e) from e

    def get_by_id(self, fine_id: str) -> Fine | None:
        try:
            model = self.session.get(FineModel, fine_id)
            return FineMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve fine', cause=e) from e

    def save(self, fine: Fine) -> Fine:
        model = self.session.get(FineModel, fine.id)
        if not model:
            model = FineMapper.from_entity(fine)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save fine', cause=e) from e
            fine.id = str(model.id)
            return fine
        model.paid_date = fine.paid_date
        model.status = FineStatus(fine.status)
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to update fine', cause=e) from e
        return fine

    def delete_by_id(self, fine_id: str) -> None:
        try:
            self.session.query(FineModel).filter_by(id=fine_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete fine', cause=e) from e
