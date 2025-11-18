from __future__ import annotations

from decimal import Decimal
import datetime

import factory

from lms.infrastructure.database.db import db_session
from lms.infrastructure.database.models.patrons import FineModel, FineStatus, PatronModel, PatronStatus
from lms.infrastructure.database.models.serials import (
    SerialModel,
    SerialStatus,
    SerialFrequency,
    SerialIssueModel,
    SerialIssueStatus,
)
from lms.infrastructure.database.models.catalogs import (
    CopyModel,
    ItemModel,
    CopyStatus,
    ItemFormat,
    AuthorModel,
    CategoryModel,
    PublisherModel,
)
from lms.infrastructure.database.models.acquisitions import (
    OrderStatus,
    VendorModel,
    VendorStatus,
    OrderLineStatus,
    AcquisitionOrderModel,
    AcquisitionOrderLineModel,
)
from lms.infrastructure.database.models.circulations import HoldModel, LoanModel, HoldStatus
from lms.infrastructure.database.models.organization import StaffRole, StaffModel, BranchModel, BranchStatus


class BranchFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BranchModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    name = factory.Faker('company')
    address = factory.Faker('address')
    phone = factory.Faker('phone_number')
    email = factory.Faker('company_email')
    manager_id = None
    status = BranchStatus.ACTIVE


class PublisherFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PublisherModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    name = factory.Faker('company')
    address = factory.Faker('address')
    email = factory.Faker('company_email')


class AuthorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AuthorModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    name = factory.Faker('name')
    bio = factory.Faker('text', max_nb_chars=200)
    birth_date = factory.Faker('date_of_birth', minimum_age=25, maximum_age=80)


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = CategoryModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=100)


class ItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ItemModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    title = factory.Faker('catch_phrase')
    isbn = factory.Faker('isbn13')
    publisher = factory.SubFactory(PublisherFactory)
    publication_year = factory.Faker('year')
    category = factory.SubFactory(CategoryFactory)
    edition = factory.Faker('word')
    format = ItemFormat.BOOK
    description = factory.Faker('text', max_nb_chars=200)


class CopyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = CopyModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    item = factory.SubFactory(ItemFactory)
    branch = factory.SubFactory(BranchFactory)
    barcode = factory.Faker('ean')
    status = CopyStatus.AVAILABLE
    location = factory.Faker('word')
    acquisition_date = factory.LazyFunction(datetime.date.today)


class PatronFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PatronModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    name = factory.Faker('name')
    email = factory.Faker('email')
    branch = factory.SubFactory(BranchFactory)
    member_since = factory.LazyFunction(datetime.date.today)
    status = PatronStatus.ACTIVE


class FineFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FineModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    patron = factory.SubFactory(PatronFactory)
    amount = factory.LazyFunction(lambda: Decimal('10.50'))
    reason = factory.Faker('sentence')
    issued_date = factory.LazyFunction(datetime.date.today)
    paid_date = None
    status = FineStatus.UNPAID


class StaffFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = StaffModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    name = factory.Faker('name')
    email = factory.Faker('email')
    role = StaffRole.LIBRARIAN
    branch = factory.SubFactory(BranchFactory)
    hire_date = factory.LazyFunction(datetime.date.today)


class LoanFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = LoanModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    copy = factory.SubFactory(CopyFactory)
    patron = factory.SubFactory(PatronFactory)
    branch = factory.SubFactory(BranchFactory)
    staff_out = factory.SubFactory(StaffFactory)
    staff_in = factory.SubFactory(StaffFactory)
    loan_date = factory.LazyFunction(datetime.date.today)
    due_date = factory.LazyFunction(lambda: datetime.date.today() + datetime.timedelta(days=14))
    return_date = None


class HoldFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = HoldModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    item = factory.SubFactory(ItemFactory)
    copy_id = None
    patron = factory.SubFactory(PatronFactory)
    loan_id = factory.Faker('uuid7')
    request_date = factory.LazyFunction(datetime.date.today)
    expiry_date = factory.LazyFunction(lambda: datetime.date.today() + datetime.timedelta(days=7))
    status = HoldStatus.PENDING


class VendorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = VendorModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    name = factory.Faker('company')
    address = factory.Faker('address')
    email = factory.Faker('company_email')
    phone = factory.Faker('phone_number')
    status = VendorStatus.ACTIVE


class AcquisitionOrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AcquisitionOrderModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    vendor = factory.SubFactory(VendorFactory)
    staff = factory.SubFactory(StaffFactory)
    order_date = factory.LazyFunction(datetime.date.today)
    received_date = None
    status = OrderStatus.PENDING


class AcquisitionOrderLineFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AcquisitionOrderLineModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    order = factory.SubFactory(AcquisitionOrderFactory)
    item = factory.SubFactory(ItemFactory)
    quantity = 1
    unit_price = factory.LazyFunction(lambda: Decimal('25.99'))
    received_quantity = None
    status = OrderLineStatus.PENDING


class SerialFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SerialModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    title = factory.Faker('catch_phrase')
    issn = factory.Faker('isbn13')
    item = factory.SubFactory(ItemFactory)
    frequency = SerialFrequency.MONTHLY
    description = factory.Faker('text', max_nb_chars=200)
    status = SerialStatus.ACTIVE


class SerialIssueFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SerialIssueModel
        sqlalchemy_session = db_session
        sqlalchemy_session_persistence = 'flush'

    serial = factory.SubFactory(SerialFactory)
    issue_number = factory.Faker('bothify', text='Issue ##')
    date_received = factory.LazyFunction(datetime.date.today)
    status = SerialIssueStatus.RECEIVED
    copy = factory.SubFactory(CopyFactory)
