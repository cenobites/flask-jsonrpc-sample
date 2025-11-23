from __future__ import annotations

import uuid
import typing as t

import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.catalogs.entities import Copy
from lms.domain.circulations.entities import Hold, Loan
from lms.infrastructure.database.models.catalogs import CopyModel, CopyStatus
from lms.infrastructure.database.models.circulations import HoldModel, LoanModel, HoldStatus
from lms.infrastructure.database.mappers.circulations import HoldMapper, LoanMapper


class SQLAlchemyLoanRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Loan]:
        models = self.session.query(LoanModel).all()
        return [LoanMapper.to_entity(m) for m in models]

    def find_by_patron_id(self, patron_id: str) -> list[Loan]:
        models = self.session.query(LoanModel).filter(LoanModel.patron_id == patron_id).all()
        return [LoanMapper.to_entity(m) for m in models]

    def get_by_id(self, loan_id: str) -> Loan | None:
        model = self.session.get(LoanModel, loan_id)
        return LoanMapper.to_entity(model) if model else None

    def save(self, loan: Loan, copy: Copy) -> Loan:
        copy_model = t.cast(CopyModel, self.session.get(CopyModel, copy.id))
        copy_model.status = CopyStatus(copy.status)

        model = self.session.get(LoanModel, loan.id)
        if not model:
            model = LoanMapper.from_entity(loan)
            self.session.add(model)
            self.session.commit()
            loan.id = str(model.id)
            return loan
        model.staff_out_id = uuid.UUID(loan.staff_out_id)
        if loan.staff_in_id:
            model.staff_in_id = uuid.UUID(loan.staff_in_id)
        model.return_date = loan.return_date
        self.session.commit()
        return loan

    def delete_by_id(self, loan_id: str) -> None:
        self.session.query(LoanModel).filter_by(id=loan_id).delete()
        self.session.commit()


class SQLAlchemyHoldRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Hold]:
        models = self.session.query(HoldModel).all()
        return [HoldMapper.to_entity(m) for m in models]

    def find_active_holds_by_patron(self, patron_id: str) -> list[Hold]:
        models = (
            self.session.query(HoldModel)
            .filter(HoldModel.patron_id == patron_id, HoldModel.status == HoldStatus.PENDING)
            .all()
        )
        return [HoldMapper.to_entity(m) for m in models]

    def find_active_holds_by_item(self, item_id: str) -> list[Hold]:
        models = (
            self.session.query(HoldModel)
            .join(CopyModel, HoldModel.copy_id == CopyModel.id)
            .filter(CopyModel.item_id == item_id, HoldModel.status == HoldStatus.PENDING)
            .all()
        )
        return [HoldMapper.to_entity(m) for m in models]

    def get_by_id(self, hold_id: str) -> Hold | None:  # signature aligned
        model = self.session.get(HoldModel, hold_id)
        return HoldMapper.to_entity(model) if model else None

    def save(self, hold: Hold) -> Hold:
        model = self.session.get(HoldModel, hold.id)
        if not model:
            model = HoldMapper.from_entity(hold)
            self.session.add(model)
            self.session.commit()
            hold.id = str(model.id)
            return hold
        model.status = HoldStatus(hold.status)
        model.expiry_date = hold.expiry_date
        self.session.commit()
        return hold

    def delete_by_id(self, hold_id: str) -> None:
        self.session.query(HoldModel).filter_by(id=hold_id).delete()
        self.session.commit()
