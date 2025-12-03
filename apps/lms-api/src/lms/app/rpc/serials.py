from __future__ import annotations

import typing as t

from flask import current_app

from flask_jsonrpc import JSONRPCBlueprint
import flask_jsonrpc.types.params as tp
import flask_jsonrpc.types.methods as tm

from lms.app.schemas import Page
from lms.app.schemas.serials import SerialCreate
from lms.app.services.serials import SerialService
from lms.app.exceptions.serials import SerialNotFoundError, SerialIssueNotFoundError
from lms.domain.serials.entities import Serial

jsonrpc_bp = JSONRPCBlueprint('serials', __name__)


@jsonrpc_bp.errorhandler(SerialNotFoundError)
def handle_serial_not_found_error(ex: SerialNotFoundError) -> dict[str, t.Any]:
    return {'message': ex.message, 'code': ex.__class__.__name__}


@jsonrpc_bp.errorhandler(SerialIssueNotFoundError)
def handle_serial_issue_not_found_error(ex: SerialIssueNotFoundError) -> dict[str, t.Any]:
    return {'message': ex.message, 'code': ex.__class__.__name__}


@jsonrpc_bp.method(
    'Serials.list',
    tm.MethodAnnotated[
        tm.Summary('List serials'),
        tm.Description('Get a list of all serials/periodicals'),
        tm.Tag(name='serials', summary='Serials Management', description='Library serials and periodicals operations'),
    ],
)
def list_serials() -> t.Annotated[Page[Serial], tp.Summary('List of serials')]:
    serial_service: SerialService = current_app.container.serial_service  # type: ignore
    serials = serial_service.find_all_serials()
    return Page[Serial](results=serials, count=len(serials))


@jsonrpc_bp.method(
    'Serials.get',
    tm.MethodAnnotated[
        tm.Summary('Get serial by ID'), tm.Description('Retrieve details of a specific serial'), tm.Tag(name='serials')
    ],
)
def get_serial(
    serial_id: t.Annotated[str, tp.Summary('Serial ID'), tp.Required()],
) -> t.Annotated[Serial, tp.Summary('Serial information')]:
    serial_service: SerialService = current_app.container.serial_service  # type: ignore
    serial = serial_service.get_serial(serial_id)
    return serial


@jsonrpc_bp.method(
    'Serials.create',
    tm.MethodAnnotated[
        tm.Summary('Create serial'), tm.Description('Create a new serial/periodical'), tm.Tag(name='serials')
    ],
)
def create_serial(
    serial: t.Annotated[SerialCreate, tp.Summary('Serial information'), tp.Required()],
) -> t.Annotated[Serial, tp.Summary('Created serial information')]:
    serial_service: SerialService = current_app.container.serial_service  # type: ignore
    created_serial = serial_service.subscribe_serial(
        title=serial.title,
        issn=serial.issn,
        item_id=serial.item_id,
        frequency=serial.frequency,
        description=serial.description,
    )
    return created_serial
