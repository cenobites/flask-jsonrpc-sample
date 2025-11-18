from __future__ import annotations

import uuid

from lms.domain.circulations.entities import Hold, Loan, HoldStatus

from ..models.circulations import HoldModel, LoanModel


class LoanMapper:
    @staticmethod
    def to_entity(model: LoanModel) -> Loan:
        return Loan(
            id=str(model.id) if model.id else None,
            copy_id=str(model.copy_id),
            patron_id=str(model.patron_id),
            staff_out_id=str(model.staff_out_id),
            staff_in_id=str(model.staff_in_id) if model.staff_in_id else None,
            branch_id=str(model.branch_id),
            loan_date=model.loan_date,
            due_date=model.due_date,
            return_date=model.return_date,
        )

    @staticmethod
    def from_entity(entity: Loan) -> LoanModel:
        model = LoanModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.copy_id = uuid.UUID(entity.copy_id)
        model.patron_id = uuid.UUID(entity.patron_id)
        model.staff_out_id = uuid.UUID(entity.staff_out_id)
        model.staff_in_id = uuid.UUID(entity.staff_in_id) if entity.staff_in_id else None
        model.branch_id = uuid.UUID(entity.branch_id)
        model.loan_date = entity.loan_date
        model.due_date = entity.due_date
        model.return_date = entity.return_date
        return model


class HoldMapper:
    @staticmethod
    def to_entity(model: HoldModel) -> Hold:
        return Hold(
            id=str(model.id) if model.id else None,
            item_id=str(model.item_id),
            copy_id=str(model.copy_id),
            patron_id=str(model.patron_id),
            request_date=model.request_date,
            expiry_date=model.expiry_date,
            status=model.status.value,
        )

    @staticmethod
    def from_entity(entity: Hold) -> HoldModel:
        model = HoldModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.item_id = uuid.UUID(entity.item_id)
        model.copy_id = uuid.UUID(entity.copy_id)
        model.patron_id = uuid.UUID(entity.patron_id)
        model.request_date = entity.request_date
        model.expiry_date = entity.expiry_date
        model.status = HoldStatus(entity.status)
        return model
