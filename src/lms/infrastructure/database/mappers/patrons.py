from __future__ import annotations

import uuid

from lms.domain.patrons.entities import Fine, Patron
from lms.infrastructure.database.models.patrons import FineModel, FineStatus, PatronModel, PatronStatus


class PatronMapper:
    @staticmethod
    def to_entity(model: PatronModel) -> Patron:
        return Patron(
            id=str(model.id) if model.id else None,
            name=model.name,
            email=model.email,
            branch_id=str(model.branch_id),
            status=model.status.value,
            member_since=model.member_since,
        )

    @staticmethod
    def from_entity(entity: Patron) -> PatronModel:
        model = PatronModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.name = entity.name
        model.email = entity.email
        model.branch_id = uuid.UUID(entity.branch_id)
        model.status = PatronStatus(entity.status)
        model.member_since = entity.member_since
        return model


class FineMapper:
    @staticmethod
    def to_entity(model: FineModel) -> Fine:
        return Fine(
            id=str(model.id) if model.id else None,
            patron_id=str(model.patron_id),
            loan_id='',  # str(model.loan_id),
            amount=model.amount,
            reason=model.reason,
            issued_date=model.issued_date,
            paid_date=model.paid_date,
            status=model.status.value,
        )

    @staticmethod
    def from_entity(entity: Fine) -> FineModel:
        model = FineModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.patron_id = uuid.UUID(entity.patron_id)
        # model.loan_id = uuid.UUID(entity.loan_id)
        model.amount = entity.amount
        model.reason = entity.reason
        model.issued_date = entity.issued_date
        model.paid_date = entity.paid_date
        model.status = FineStatus(entity.status)
        return model
