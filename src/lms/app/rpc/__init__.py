from __future__ import annotations

from flask import Flask

from flask_jsonrpc import JSONRPC


def register(app: Flask, jsonrpc: JSONRPC) -> None:
    from . import patrons, serials, catalogs, acquisitions, circulations, organizations

    jsonrpc.register_blueprint(app, patrons.jsonrpc_bp, url_prefix='/patrons', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(
        app, organizations.jsonrpc_bp, url_prefix='/organizations', enable_web_browsable_api=True
    )
    jsonrpc.register_blueprint(app, catalogs.jsonrpc_bp, url_prefix='/catalogs', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(app, circulations.jsonrpc_bp, url_prefix='/circulations', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(app, acquisitions.jsonrpc_bp, url_prefix='/acquisitions', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(app, serials.jsonrpc_bp, url_prefix='/serials', enable_web_browsable_api=True)
