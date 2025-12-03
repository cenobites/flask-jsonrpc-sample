from __future__ import annotations

import typing as t

from flask import Flask


class Container:
    def __init__(self) -> None:
        self._providers: dict[str, tuple[t.Callable[[], t.Any], bool]] = {}
        self.singleton_deps: dict[str, t.Any] = {}

    def register_singleton(self, name: str, factory: t.Callable[[], t.Any]) -> None:  # noqa: ANN401
        self._providers[name] = (factory, True)

    def register_factory(self, name: str, factory: t.Callable[[], t.Any]) -> None:
        self._providers[name] = (factory, False)

    def resolve(self, name: str) -> t.Any:  # noqa: ANN401
        if name in self.singleton_deps:
            return self.singleton_deps[name]
        if name in self._providers:
            factory, is_singleton = self._providers[name]
            if is_singleton:
                instance = factory()
                self.singleton_deps[name] = instance
                return instance
            return factory()
        raise AttributeError(f"Dependency '{name}' not found in container.")

    def __getattr__(self, name: str) -> t.Any:  # noqa: ANN401
        return self.resolve(name)


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
    from lms.app.services.organizations import StaffService, BranchService
    from lms.infrastructure.database.db import db_session
    from lms.domain.circulations.services import HoldPolicyService, LoanPolicyService
    from lms.domain.organizations.services import (
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
    from lms.infrastructure.database.repositories.organizations import (
        SQLAlchemyStaffRepository,
        SQLAlchemyBranchRepository,
    )

    container = Container()
    container.register_singleton('db_session', db_session)

    # Acquisition Repositories
    container.register_singleton(
        'vendor_repository', lambda: SQLAlchemyVendorRepository(container.resolve('db_session'))
    )
    container.register_singleton(
        'acquisition_order_repository', lambda: SQLAlchemyAcquisitionOrderRepository(container.resolve('db_session'))
    )
    container.register_singleton(
        'acquisition_order_line_repository',
        lambda: SQLAlchemyAcquisitionOrderLineRepository(container.resolve('db_session')),
    )

    # Catalog Repositories
    container.register_singleton('item_repository', lambda: SQLAlchemyItemRepository(container.resolve('db_session')))
    container.register_singleton('copy_repository', lambda: SQLAlchemyCopyRepository(container.resolve('db_session')))
    container.register_singleton(
        'author_repository', lambda: SQLAlchemyAuthorRepository(container.resolve('db_session'))
    )
    container.register_singleton(
        'category_repository', lambda: SQLAlchemyCategoryRepository(container.resolve('db_session'))
    )
    container.register_singleton(
        'publisher_repository', lambda: SQLAlchemyPublisherRepository(container.resolve('db_session'))
    )

    # Circulations Repositories
    container.register_singleton('loan_repository', lambda: SQLAlchemyLoanRepository(container.resolve('db_session')))
    container.register_singleton('hold_repository', lambda: SQLAlchemyHoldRepository(container.resolve('db_session')))

    # Organization Repositories
    container.register_singleton('staff_repository', lambda: SQLAlchemyStaffRepository(container.resolve('db_session')))
    container.register_singleton(
        'branch_repository', lambda: SQLAlchemyBranchRepository(container.resolve('db_session'))
    )

    # Patrons Repositories
    container.register_singleton(
        'patron_repository', lambda: SQLAlchemyPatronRepository(container.resolve('db_session'))
    )
    container.register_singleton('fine_repository', lambda: SQLAlchemyFineRepository(container.resolve('db_session')))

    # Serials Repositories
    container.register_singleton(
        'serial_repository', lambda: SQLAlchemySerialRepository(container.resolve('db_session'))
    )
    container.register_singleton(
        'serial_issue_repository', lambda: SQLAlchemySerialIssueRepository(container.resolve('db_session'))
    )

    # Services instantiation
    container.register_singleton(
        'contaitem_service',
        lambda: ItemService(
            item_repository=container.resolve('item_repository'), copy_repository=container.resolve('copy_repository')
        ),
    )
    container.register_singleton(
        'author_service', lambda: AuthorService(author_repository=container.resolve('author_repository'))
    )
    container.register_singleton(
        'category_service', lambda: CategoryService(category_repository=container.resolve('category_repository'))
    )
    container.register_singleton(
        'publisher_service', lambda: PublisherService(publisher_repository=container.resolve('publisher_repository'))
    )

    # Acquisition Services
    container.register_singleton(
        'vendor_service', lambda: VendorService(vendor_repository=container.resolve('vendor_repository'))
    )
    container.register_singleton(
        'acquisition_order_service',
        lambda: AcquisitionOrderService(
            acquisition_order_repository=container.resolve('acquisition_order_repository'),
            acquisition_order_line_repository=container.resolve('acquisition_order_line_repository'),
        ),
    )

    # Patron Services
    container.register_singleton(
        'patron_uniqueness_service',
        lambda: PatronUniquenessService(patron_repository=container.resolve('patron_repository')),
    )
    container.register_singleton(
        'patron_reinstatement_service',
        lambda: PatronReinstatementService(
            patron_repository=container.resolve('patron_repository'),
            loan_repository=container.resolve('loan_repository'),
        ),
    )
    container.register_singleton(
        'fine_policy_service',
        lambda: FinePolicyService(
            copy_repository=container.resolve('copy_repository'), item_repository=container.resolve('item_repository')
        ),
    )

    # Circulation Services
    container.register_singleton('loan_policy_service', lambda: LoanPolicyService())
    container.register_singleton(
        'hold_policy_service', lambda: HoldPolicyService(hold_repository=container.resolve('hold_repository'))
    )
    container.register_singleton(
        'patron_holding_service', lambda: PatronHoldingService(hold_repository=container.resolve('hold_repository'))
    )
    container.register_singleton(
        'patron_barring_service',
        lambda: PatronBarringService(
            patron_repository=container.resolve('patron_repository'),
            loan_repository=container.resolve('loan_repository'),
        ),
    )

    # Catalog Services
    container.register_singleton(
        'copy_service', lambda: CopyService(copy_repository=container.resolve('copy_repository'))
    )

    container.register_singleton(
        'loan_service',
        lambda: LoanService(
            loan_repository=container.resolve('loan_repository'),
            patron_repository=container.resolve('patron_repository'),
            branch_repository=container.resolve('branch_repository'),
            staff_repository=container.resolve('staff_repository'),
            copy_repository=container.resolve('copy_repository'),
            loan_policy_service=container.resolve('loan_policy_service'),
            patron_barring_service=container.resolve('patron_barring_service'),
        ),
    )
    container.register_singleton(
        'hold_service',
        lambda: HoldService(
            hold_repository=container.resolve('hold_repository'),
            patron_repository=container.resolve('patron_repository'),
            item_repository=container.resolve('item_repository'),
            branch_repository=container.resolve('branch_repository'),
            patron_holding_service=container.resolve('patron_holding_service'),
            hold_policy_service=container.resolve('hold_policy_service'),
            patron_barring_service=container.resolve('patron_barring_service'),
            loan_policy_service=container.resolve('loan_policy_service'),
            staff_repository=container.resolve('staff_repository'),
            loan_repository=container.resolve('loan_repository'),
            copy_repository=container.resolve('copy_repository'),
        ),
    )

    container.register_singleton(
        'serial_service',
        lambda: SerialService(
            serial_repository=container.resolve('serial_repository'),
            serial_issue_repository=container.resolve('serial_issue_repository'),
            item_repository=container.resolve('item_repository'),
        ),
    )
    container.register_singleton(
        'fine_service',
        lambda: FineService(
            fine_repository=container.resolve('fine_repository'),
            fine_policy_service=container.resolve('fine_policy_service'),
        ),
    )
    container.register_singleton(
        'patron_service',
        lambda: PatronService(
            patron_repository=container.resolve('patron_repository'),
            patron_uniqueness_service=container.resolve('patron_uniqueness_service'),
            patron_reinstatement_service=container.resolve('patron_reinstatement_service'),
        ),
    )

    container.register_singleton(
        'branch_uniqueness_service',
        lambda: BranchUniquenessService(branch_repository=container.resolve('branch_repository')),
    )
    container.register_singleton(
        'branch_assignment_service',
        lambda: BranchAssignmentService(
            branch_repository=container.resolve('branch_repository'),
            staff_repository=container.resolve('staff_repository'),
        ),
    )
    container.register_singleton(
        'branch_service',
        lambda: BranchService(
            branch_repository=container.resolve('branch_repository'),
            branch_uniqueness_service=container.resolve('branch_uniqueness_service'),
            branch_assignment_service=container.resolve('branch_assignment_service'),
        ),
    )

    container.register_singleton(
        'staff_uniqueness_service',
        lambda: StaffUniquenessService(staff_repository=container.resolve('staff_repository')),
    )
    container.register_singleton(
        'staff_service',
        lambda: StaffService(
            staff_repository=container.resolve('staff_repository'),
            staff_uniqueness_service=container.resolve('staff_uniqueness_service'),
        ),
    )
    app.container = container  # type: ignore
