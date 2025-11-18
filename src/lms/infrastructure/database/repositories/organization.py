from __future__ import annotations

import uuid

import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.domain.organization.entities import Staff, Branch
from lms.infrastructure.database.models.organization import StaffRole, StaffModel, BranchModel, BranchStatus
from lms.infrastructure.database.mappers.organization import StaffMapper, BranchMapper


class SQLAlchemyBranchRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Branch]:
        models = self.session.query(BranchModel).all()
        return [BranchMapper.to_entity(m) for m in models]

    def get_by_id(self, branch_id: str) -> Branch | None:
        model = self.session.get(BranchModel, branch_id)
        return BranchMapper.to_entity(model) if model else None

    def exists_by_name(self, name: str) -> bool:
        q = self.session.query(BranchModel).filter_by(name=name)
        return self.session.query(q.exists()).scalar()

    def save(self, branch: Branch) -> Branch:
        model = self.session.get(BranchModel, branch.id) if branch.id else None
        if not model:
            model = BranchMapper.from_entity(branch)
            self.session.add(model)
            self.session.commit()
            branch.id = str(model.id)
            return branch
        model.name = branch.name
        model.address = branch.address
        model.phone = branch.phone
        model.email = branch.email
        model.manager_id = uuid.UUID(branch.manager_id) if branch.manager_id else None
        model.status = BranchStatus(branch.status)
        self.session.commit()
        return branch

    def delete_by_id(self, branch_id: str) -> None:
        self.session.query(BranchModel).filter_by(id=branch_id).delete()
        self.session.commit()


class SQLAlchemyStaffRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Staff]:
        models = self.session.query(StaffModel).all()
        return [StaffMapper.to_entity(m) for m in models]

    def get_by_id(self, staff_id: str) -> Staff | None:
        model = self.session.get(StaffModel, staff_id)
        return StaffMapper.to_entity(model) if model else None

    def exists_by_email(self, email: str) -> bool:
        q = self.session.query(StaffModel).filter_by(email=email)
        return self.session.query(q.exists()).scalar()

    def save(self, staff: Staff) -> Staff:
        model = self.session.get(StaffModel, staff.id) if staff.id else None
        if not model:
            model = StaffMapper.from_entity(staff)
            self.session.add(model)
            self.session.commit()
            staff.id = str(model.id)
            return staff
        model.name = staff.name
        model.email = staff.email
        model.role = StaffRole(staff.role)
        model.branch_id = uuid.UUID(staff.branch_id) if staff.branch_id else None
        self.session.commit()
        return staff

    def delete_by_id(self, staff_id: str) -> None:
        self.session.query(StaffModel).filter_by(id=staff_id).delete()
        self.session.commit()
