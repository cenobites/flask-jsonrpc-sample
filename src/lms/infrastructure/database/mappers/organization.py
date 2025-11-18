from __future__ import annotations

import uuid

from lms.domain.organization.entities import Staff, Branch
from lms.infrastructure.database.models.organization import (
    StaffRole,
    StaffModel,
    BranchModel,
    StaffStatus,
    BranchStatus,
)


class BranchMapper:
    @staticmethod
    def to_entity(model: BranchModel) -> Branch:
        return Branch(
            id=str(model.id) if model.id else None,
            name=model.name,
            address=model.address,
            phone=model.phone,
            email=model.email,
            manager_id=str(model.manager_id) if model.manager_id else None,
            status=model.status.value,
        )

    @staticmethod
    def from_entity(entity: Branch) -> BranchModel:
        model = BranchModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        if entity.manager_id:
            model.manager_id = uuid.UUID(entity.manager_id)
        model.name = entity.name
        model.address = entity.address
        model.phone = entity.phone
        model.email = entity.email
        model.status = BranchStatus(entity.status)
        return model


class StaffMapper:
    @staticmethod
    def to_entity(model: StaffModel) -> Staff:
        return Staff(
            id=str(model.id) if model.id else None,
            name=model.name,
            email=model.email,
            role=model.role.value,
            branch_id=str(model.branch_id) if model.branch_id else None,
            status=model.status.value,
        )

    @staticmethod
    def from_entity(entity: Staff) -> StaffModel:
        model = StaffModel()
        if entity.id:
            model.id = uuid.UUID(entity.id)
        model.branch_id = uuid.UUID(entity.branch_id) if entity.branch_id else None
        model.name = entity.name
        model.email = entity.email
        model.role = StaffRole(entity.role)
        model.status = StaffStatus(entity.status)
        return model
