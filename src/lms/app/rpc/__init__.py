from __future__ import annotations

from flask import Flask

from flask_jsonrpc import JSONRPC


def register(app: Flask, jsonrpc: JSONRPC) -> None:
    from . import patrons, serials, catalogs, acquisitions, circulations, organization

    jsonrpc.register_blueprint(app, patrons.jsonrpc_bp, url_prefix='/patrons', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(app, organization.jsonrpc_bp, url_prefix='/organization', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(app, catalogs.jsonrpc_bp, url_prefix='/catalog', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(app, circulations.jsonrpc_bp, url_prefix='/circulation', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(app, acquisitions.jsonrpc_bp, url_prefix='/acquisition', enable_web_browsable_api=True)
    jsonrpc.register_blueprint(app, serials.jsonrpc_bp, url_prefix='/serial', enable_web_browsable_api=True)
