from __future__ import annotations

from flask import Flask


class Container:
    def __init__(self, deps: dict) -> None:
        self.singleton_deps = deps

    def __getattr__(self, name: str) -> object:
        if name in self.singleton_deps:
            return lambda: self.singleton_deps[name]
        raise AttributeError(f"Dependency '{name}' not found in container.")


def register(app: Flask) -> None:
    from lms.app.services.patrons import FineService, PatronService
    from lms.app.services.serials import SerialService
    from lms.app.services.catalogs import CopyService, ItemService, AuthorService, CategoryService, PublisherService
    from lms.domain.patrons.services import (
        FinePolicyService,
        PatronBarringService,
        PatronHoldingService,
        PatronUniquenessService,
        PatronReinstatementService,
    )
    from lms.app.services.acquisitions import VendorService, AcquisitionOrderService
    from lms.app.services.circulations import HoldService, LoanService
    from lms.app.services.organization import StaffService, BranchService
    from lms.infrastructure.database.db import db_session
    from lms.domain.circulations.services import HoldPolicyService, LoanPolicyService
    from lms.domain.organization.services import (
        StaffUniquenessService,
        BranchAssignmentService,
        BranchUniquenessService,
    )
    from lms.infrastructure.database.repositories.patrons import SQLAlchemyFineRepository, SQLAlchemyPatronRepository
    from lms.infrastructure.database.repositories.serials import (
        SQLAlchemySerialRepository,
        SQLAlchemySerialIssueRepository,
    )
    from lms.infrastructure.database.repositories.catalogs import (
        SQLAlchemyCopyRepository,
        SQLAlchemyItemRepository,
        SQLAlchemyAuthorRepository,
        SQLAlchemyCategoryRepository,
        SQLAlchemyPublisherRepository,
    )
    from lms.infrastructure.database.repositories.acquisitions import (
        SQLAlchemyVendorRepository,
        SQLAlchemyAcquisitionOrderRepository,
        SQLAlchemyAcquisitionOrderLineRepository,
    )
    from lms.infrastructure.database.repositories.circulations import SQLAlchemyHoldRepository, SQLAlchemyLoanRepository
    from lms.infrastructure.database.repositories.organization import (
        SQLAlchemyStaffRepository,
        SQLAlchemyBranchRepository,
    )

    # Acquisition Repositories
    vendor_repository = SQLAlchemyVendorRepository(db_session)
    acquisition_order_repository = SQLAlchemyAcquisitionOrderRepository(db_session)
    acquisition_order_line_repository = SQLAlchemyAcquisitionOrderLineRepository(db_session)

    # Catalog Repositories
    item_repository = SQLAlchemyItemRepository(db_session)
    copy_repository = SQLAlchemyCopyRepository(db_session)
    author_repository = SQLAlchemyAuthorRepository(db_session)
    category_repository = SQLAlchemyCategoryRepository(db_session)
    publisher_repository = SQLAlchemyPublisherRepository(db_session)

    # Circulations Repositories
    loan_repository = SQLAlchemyLoanRepository(db_session)
    hold_repository = SQLAlchemyHoldRepository(db_session)

    # Organization Repositories
    staff_repository = SQLAlchemyStaffRepository(db_session)
    branch_repository = SQLAlchemyBranchRepository(db_session)

    # Patrons Repositories
    patron_repository = SQLAlchemyPatronRepository(db_session)
    fine_repository = SQLAlchemyFineRepository(db_session)

    # Serials Repositories
    serial_repository = SQLAlchemySerialRepository(db_session)
    serial_issue_repository = SQLAlchemySerialIssueRepository(db_session)

    item_service = ItemService(item_repository=item_repository, copy_repository=copy_repository)
    author_service = AuthorService(author_repository=author_repository)
    category_service = CategoryService(category_repository=category_repository)
    publisher_service = PublisherService(publisher_repository=publisher_repository)

    # Acquisition Services
    vendor_service = VendorService(vendor_repository=vendor_repository)
    acquisition_order_service = AcquisitionOrderService(
        acquisition_order_repository=acquisition_order_repository,
        acquisition_order_line_repository=acquisition_order_line_repository,
    )

    copy_repository = SQLAlchemyCopyRepository(db_session)

    patron_uniqueness_service = PatronUniquenessService(patron_repository=patron_repository)
    patron_reinstatement_service = PatronReinstatementService(
        patron_repository=patron_repository, loan_repository=loan_repository
    )
    fine_policy_service = FinePolicyService(copy_repository=copy_repository, item_repository=item_repository)

    loan_policy_service = LoanPolicyService()
    hold_policy_service = HoldPolicyService(hold_repository=hold_repository)
    patron_holding_service = PatronHoldingService(hold_repository=hold_repository)
    patron_barring_service = PatronBarringService(patron_repository=patron_repository, loan_repository=loan_repository)

    copy_service = CopyService(copy_repository=copy_repository)

    loan_service = LoanService(
        loan_repository=loan_repository,
        patron_repository=patron_repository,
        branch_repository=branch_repository,
        staff_repository=staff_repository,
        copy_repository=copy_repository,
        loan_policy_service=loan_policy_service,
        patron_barring_service=patron_barring_service,
    )
    hold_service = HoldService(
        hold_repository=hold_repository,
        patron_repository=patron_repository,
        item_repository=item_repository,
        branch_repository=branch_repository,
        patron_holding_service=patron_holding_service,
        hold_policy_service=hold_policy_service,
        patron_barring_service=patron_barring_service,
        loan_policy_service=loan_policy_service,
        staff_repository=staff_repository,
        loan_repository=loan_repository,
        copy_repository=copy_repository,
    )

    serial_service = SerialService(serial_repository=serial_repository, serial_issue_repository=serial_issue_repository)
    fine_service = FineService(fine_repository=fine_repository, fine_policy_service=fine_policy_service)

    patron_service = PatronService(
        patron_repository=patron_repository,
        patron_uniqueness_service=patron_uniqueness_service,
        patron_reinstatement_service=patron_reinstatement_service,
    )

    branch_uniqueness_service = BranchUniquenessService(branch_repository=branch_repository)
    branch_assignment_service = BranchAssignmentService(
        branch_repository=branch_repository, staff_repository=staff_repository
    )
    branch_service = BranchService(
        branch_repository=branch_repository,
        branch_uniqueness_service=branch_uniqueness_service,
        branch_assignment_service=branch_assignment_service,
    )

    staff_uniqueness_service = StaffUniquenessService(staff_repository=staff_repository)
    staff_service = StaffService(staff_repository=staff_repository, staff_uniqueness_service=staff_uniqueness_service)

    app.container = Container(  # type: ignore
        {
            'vendor_repository': vendor_repository,
            'acquisition_order_repository': acquisition_order_repository,
            'acquisition_order_line_repository': acquisition_order_line_repository,
            'item_repository': item_repository,
            'copy_repository': copy_repository,
            'copy_service': copy_service,
            'author_repository': author_repository,
            'category_repository': category_repository,
            'publisher_repository': publisher_repository,
            'loan_repository': loan_repository,
            'hold_repository': hold_repository,
            'staff_repository': staff_repository,
            'branch_repository': branch_repository,
            'patron_repository': patron_repository,
            'fine_repository': fine_repository,
            'serial_repository': serial_repository,
            'serial_issue_repository': serial_issue_repository,
            'item_service': item_service,
            'author_service': author_service,
            'category_service': category_service,
            'publisher_service': publisher_service,
            'vendor_service': vendor_service,
            'acquisition_order_service': acquisition_order_service,
            'loan_service': loan_service,
            'hold_service': hold_service,
            'serial_service': serial_service,
            'fine_service': fine_service,
            'patron_service': patron_service,
            'branch_service': branch_service,
            'staff_service': staff_service,
            'patron_barring_service': patron_barring_service,
            'patron_uniqueness_service': patron_uniqueness_service,
            'patron_reinstatement_service': patron_reinstatement_service,
            'fine_policy_service': fine_policy_service,
            'loan_policy_service': loan_policy_service,
            'hold_policy_service': hold_policy_service,
            'patron_holding_service': patron_holding_service,
            'branch_uniqueness_service': branch_uniqueness_service,
            'branch_assignment_service': branch_assignment_service,
            'staff_uniqueness_service': staff_uniqueness_service,
        }
    )
