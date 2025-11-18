from __future__ import annotations

import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.patrons.entities import Fine, Patron

from ..models.patrons import FineModel, FineStatus, PatronModel, PatronStatus
from ..mappers.patrons import FineMapper, PatronMapper


class SQLAlchemyPatronRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Patron]:
        models = self.session.query(PatronModel).all()
        return [PatronMapper.to_entity(m) for m in models]

    def get_by_id(self, patron_id: str) -> Patron | None:
        model = self.session.get(PatronModel, patron_id)
        return PatronMapper.to_entity(model) if model else None

    def exists_by_email(self, email: str) -> bool:
        q = self.session.query(PatronModel).filter_by(email=email)
        return self.session.query(q.exists()).scalar()

    def save(self, patron: Patron) -> Patron:
        model = self.session.get(PatronModel, patron.id)
        if not model:
            model = PatronMapper.from_entity(patron)
            self.session.add(model)
            self.session.commit()
            patron.id = str(model.id)
            return patron
        model.name = patron.name
        model.email = patron.email
        model.status = PatronStatus(patron.status)
        self.session.commit()
        return patron

    def delete_by_id(self, patron_id: str) -> None:
        self.session.query(PatronModel).filter_by(id=patron_id).delete()
        self.session.commit()


class SQLAlchemyFineRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Fine]:
        models = self.session.query(FineModel).all()
        return [FineMapper.to_entity(m) for m in models]

    def get_by_id(self, fine_id: str) -> Fine | None:
        model = self.session.get(FineModel, fine_id)
        return FineMapper.to_entity(model) if model else None

    def save(self, fine: Fine) -> Fine:
        model = self.session.get(FineModel, fine.id)
        if not model:
            model = FineMapper.from_entity(fine)
            self.session.add(model)
            self.session.commit()
            fine.id = str(model.id)
            return fine
        model.paid_date = fine.paid_date
        model.status = FineStatus(fine.status)
        self.session.commit()
        return fine

    def delete_by_id(self, fine_id: str) -> None:
        self.session.query(FineModel).filter_by(id=fine_id).delete()
        self.session.commit()
