from __future__ import annotations

from flask import Flask


def register(app: Flask) -> None:
    from . import monitoring

    app.register_blueprint(monitoring.bp, url_prefix='/monitoring')
