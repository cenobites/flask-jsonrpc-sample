from __future__ import annotations

import uuid
from datetime import datetime
from operator import attrgetter

from flask_jsonrpc import JSONRPC
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import CHAR, DateTime, TypeDecorator
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.dialects.postgresql import UUID


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type or MSSQL's UNIQUEIDENTIFIER,
    otherwise uses CHAR(32), storing as stringified hex values.

    """

    impl = CHAR
    cache_ok = True

    _default_type = CHAR(32)
    _uuid_as_str = attrgetter('hex')

    def load_dialect_impl(self, dialect):  # noqa: ANN001, ANN202
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        elif dialect.name == 'mssql':
            return dialect.type_descriptor(UNIQUEIDENTIFIER())
        else:
            return dialect.type_descriptor(self._default_type)

    def process_bind_param(self, value, dialect):  # noqa: ANN001, ANN202
        if value is None or dialect.name in ('postgresql', 'mssql'):
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return self._uuid_as_str(value)

    def process_result_value(self, value, dialect):  # noqa: ANN001, ANN202
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class GUIDHyphens(GUID):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type or MSSQL's UNIQUEIDENTIFIER,
    otherwise uses CHAR(36), storing as stringified uuid values.

    """

    _default_type = CHAR(36)
    _uuid_as_str = str


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.Model.registry.update_type_annotation_map(  # type: ignore
    {datetime: DateTime(timezone=True), uuid.UUID: GUID}
)

jsonrpc = JSONRPC(path='/api', enable_web_browsable_api=True)

__all__ = ['db', 'jsonrpc']
