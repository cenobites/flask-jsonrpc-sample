from __future__ import annotations

from flask import Flask

from lms.config import Config
from lms.app.json import MsgSpecJSONProvider


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json = MsgSpecJSONProvider(app)

    from lms.app.extensions import db, cors, alembic, jsonrpc

    db.init_app(app)
    alembic.init_app(app)
    jsonrpc.init_app(app)
    cors.init_app(app, resources={r'/api/*': {'origins': '*'}})

    from lms.app import rpc, errors, routes, handlers, services

    services.register(app)
    handlers.register(app)
    routes.register(app)
    rpc.register(app, jsonrpc)
    errors.register(app, jsonrpc)

    @app.teardown_appcontext
    def shutdown_session(exception: BaseException | None = None) -> None:
        db.session.remove()

    return app
