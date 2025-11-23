from __future__ import annotations

import typing as t

from flask import Flask
from flask.testing import FlaskClient

import pytest

from lms.app import create_app
from lms.config import Config as BaseConfig
from lms.app.extensions import db


class Config(BaseConfig):
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'testkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


@pytest.fixture(scope='function')
def app() -> t.Generator[Flask]:
    app = create_app(Config)

    with app.app_context():
        from lms.infrastructure.database.models import (  # noqa: F401
            patrons,
            serials,
            catalogs,
            acquisitions,
            circulations,
            organizations,
        )

        db.create_all()

        yield app

        db.session.remove()
        db.session.close()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app: Flask) -> t.Generator[FlaskClient]:
    with app.test_client() as client:
        yield client
