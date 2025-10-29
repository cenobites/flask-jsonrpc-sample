from __future__ import annotations

from flask import Flask


def register(app: Flask) -> None:
    from . import patrons, catalogs, organization

    organization.register_handler(app)
    patrons.register_handler(app)
    catalogs.register_handler(app)
