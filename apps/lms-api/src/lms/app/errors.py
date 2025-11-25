from __future__ import annotations

import typing as t

from flask import Flask, Response, jsonify

from flask_jsonrpc import JSONRPC

from lms.domain import DomainError, DomainNotFound
from lms.infrastructure import InfrastructureError
from lms.infrastructure.logging import logger

from .exceptions import ServiceFailed, ApplicationError


def register(app: Flask, jsonrpc: JSONRPC) -> None:
    @jsonrpc.errorhandler(DomainNotFound)
    def handle_domain_not_found(ex: DomainNotFound) -> tuple[dict[str, t.Any], int]:
        return {'error': str(ex), 'code': ex.__class__.__name__}, 404

    @jsonrpc.errorhandler(DomainError)
    def handle_domain_error(ex: DomainError) -> tuple[dict[str, t.Any], int]:
        return {'error': str(ex), 'code': ex.__class__.__name__}, 400

    @jsonrpc.errorhandler(ServiceFailed)
    def handle_service_failed(ex: ServiceFailed) -> tuple[dict[str, t.Any], int]:
        logger.error('Service failed: %s -> %s', str(ex), str(ex.cause))
        return {'error': str(ex), 'code': ex.__class__.__name__}, ex.code

    @jsonrpc.errorhandler(ApplicationError)
    def handle_application_error(ex: ApplicationError) -> tuple[dict[str, t.Any], int]:
        logger.error('Application error: %s', str(ex))
        return {'error': str(ex), 'code': ex.__class__.__name__}, ex.code

    @jsonrpc.errorhandler(InfrastructureError)
    def handle_infrastructure_error(exc: InfrastructureError) -> tuple[dict[str, t.Any], int]:
        logger.exception(exc)
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc: Exception) -> tuple[Response, int]:
        logger.exception(exc)
        return jsonify({'error': 'Unexpected error'}), 500
