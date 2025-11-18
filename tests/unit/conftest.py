from __future__ import annotations

import typing as t

from flask import Flask
from flask.testing import FlaskClient

import pytest

from lms.config import Config as BaseConfig
from lms.app.main import create_app
from lms.app.extentions import db


class Config(BaseConfig):
    TESTING = True
    DEBUG = False
    SECRET_KEY = 'testkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


@pytest.fixture(scope='session')
def sqlalchemy_connect_url() -> str:
    return Config.SQLALCHEMY_DATABASE_URI


@pytest.fixture()
def app() -> t.Generator[Flask]:
    app = create_app(Config)

    import lms.infrastructure.database.models  # noqa: F401

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.session.close()
        db.drop_all()


@pytest.fixture()
def client(app: Flask) -> t.Generator[FlaskClient]:
    with app.test_client() as client:
        yield client
