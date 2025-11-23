from __future__ import annotations

from flask import Flask

from lms.app.extensions import db

db_session = db.session


class BaseModel(db.Model):  # type: ignore
    __abstract__ = True


def init_db(app: Flask) -> None:
    from lms.infrastructure.database.models import (  # noqa: F401
        patrons,
        serials,
        catalogs,
        acquisitions,
        circulations,
        organizations,
    )

    with app.app_context():
        db.create_all()
