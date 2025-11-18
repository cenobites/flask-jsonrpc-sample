from __future__ import annotations

from flask import Flask

from lms.config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    from lms.app.extentions import db, jsonrpc

    db.init_app(app)
    jsonrpc.init_app(app)

    from lms.app import rpc, routes, handlers, services

    services.register(app)
    handlers.register(app)
    routes.register(app)
    rpc.register(app, jsonrpc)

    return app
