from __future__ import annotations

import uuid

import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask_sqlalchemy.session import Session

from lms.infrastructure.database import RepositoryError
from lms.domain.organizations.entities import Staff, Branch
from lms.infrastructure.database.models.organizations import StaffRole, StaffModel, BranchModel, BranchStatus
from lms.infrastructure.database.mappers.organizations import StaffMapper, BranchMapper


class SQLAlchemyBranchRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Branch]:
        try:
            models = self.session.query(BranchModel).all()
            return [BranchMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve branches', cause=e) from e

    def get_by_id(self, branch_id: str) -> Branch | None:
        try:
            model = self.session.get(BranchModel, branch_id)
            return BranchMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve branch', cause=e) from e

    def exists_by_name(self, name: str) -> bool:
        try:
            q = self.session.query(BranchModel).filter_by(name=name)
            count = self.session.query(q.exists()).scalar()
            return count is not None and count > 0
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to check branch existence by name', cause=e) from e

    def save(self, branch: Branch) -> Branch:
        model = self.session.get(BranchModel, branch.id) if branch.id else None
        if not model:
            model = BranchMapper.from_entity(branch)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save branch', cause=e) from e
            branch.id = str(model.id)
            return branch
        model.name = branch.name
        model.address = branch.address
        model.phone = branch.phone
        model.email = branch.email
        model.manager_id = uuid.UUID(branch.manager_id) if branch.manager_id else None
        model.status = BranchStatus(branch.status)
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to update branch', cause=e) from e
        return branch

    def delete_by_id(self, branch_id: str) -> None:
        try:
            self.session.query(BranchModel).filter_by(id=branch_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete branch', cause=e) from e


class SQLAlchemyStaffRepository:
    def __init__(self, session: sa_orm.scoped_session[Session]) -> None:
        self.session = session

    def find_all(self) -> list[Staff]:
        try:
            models = self.session.query(StaffModel).all()
            return [StaffMapper.to_entity(m) for m in models]
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve staff members', cause=e) from e

    def get_by_id(self, staff_id: str) -> Staff | None:
        try:
            model = self.session.get(StaffModel, staff_id)
            return StaffMapper.to_entity(model) if model else None
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to retrieve staff member', cause=e) from e

    def exists_by_email(self, email: str) -> bool:
        try:
            q = self.session.query(StaffModel).filter_by(email=email)
            count = self.session.query(q.exists()).scalar()
            return count is not None and count > 0
        except sa_exc.SQLAlchemyError as e:
            raise RepositoryError('Failed to check staff existence by email', cause=e) from e

    def save(self, staff: Staff) -> Staff:
        model = self.session.get(StaffModel, staff.id) if staff.id else None
        if not model:
            model = StaffMapper.from_entity(staff)
            try:
                self.session.add(model)
                self.session.commit()
            except sa_exc.SQLAlchemyError as e:
                self.session.rollback()
                raise RepositoryError('Failed to save staff member', cause=e) from e
            staff.id = str(model.id)
            return staff
        model.name = staff.name
        model.email = staff.email
        model.role = StaffRole(staff.role)
        model.branch_id = uuid.UUID(staff.branch_id) if staff.branch_id else None
        try:
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to update staff member', cause=e) from e
        return staff

    def delete_by_id(self, staff_id: str) -> None:
        try:
            self.session.query(StaffModel).filter_by(id=staff_id).delete()
            self.session.commit()
        except sa_exc.SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryError('Failed to delete staff member', cause=e) from e
