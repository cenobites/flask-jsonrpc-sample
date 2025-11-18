from __future__ import annotations

from flask import Flask

from lms.app.extentions import db

Base = db.Model
db_session = db.session


def init_db(app: Flask) -> None:
    import lms.infrastructure.database.models  # noqa: F401

    with app.app_context():
        db.create_all()
