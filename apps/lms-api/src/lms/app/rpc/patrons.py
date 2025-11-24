from __future__ import annotations

import typing as t

from flask import current_app

from flask_jsonrpc import JSONRPCBlueprint
import flask_jsonrpc.types.params as tp
import flask_jsonrpc.types.methods as tm

from lms.app.schemas import Page
from lms.app.schemas.patrons import PatronCreate, PatronUpdate
from lms.app.services.patrons import FineService, PatronService
from lms.app.exceptions.patrons import FineNotFoundError, PatronNotFoundError
from lms.domain.patrons.entities import Fine, Patron

jsonrpc_bp = JSONRPCBlueprint('patrons', __name__)


@jsonrpc_bp.errorhandler(PatronNotFoundError)
def handle_patron_not_found_error(ex: PatronNotFoundError) -> dict[str, t.Any]:
    return {'message': ex.message, 'code': ex.__class__.__name__}


@jsonrpc_bp.errorhandler(FineNotFoundError)
def handle_fine_not_found_error(ex: FineNotFoundError) -> dict[str, t.Any]:
    return {'message': ex.message, 'code': ex.__class__.__name__}


@jsonrpc_bp.method(
    'Patrons.list',
    tm.MethodAnnotated[
        tm.Summary('List patrons'),
        tm.Description('Retrieve all patrons'),
        tm.Tag(name='patrons'),
        tm.Example(name='list_patrons_example', params=[]),
    ],
)
def list_patrons() -> t.Annotated[Page[Patron], tp.Summary('Patron list')]:
    patron_service: PatronService = current_app.container.patron_service()  # type: ignore
    patrons = patron_service.find_all_patrons()
    return Page[Patron](results=patrons, count=len(patrons))


@jsonrpc_bp.method(
    'Patrons.get',
    tm.MethodAnnotated[
        tm.Summary('Get patron by ID'),
        tm.Description('Retrieve patron information using unique ID'),
        tm.Tag(name='patrons'),
        tm.Error(code=-32002, message='Patron not found', data={'reason': 'invalid patron ID'}),
        tm.Example(name='get_patron_example', params=[tm.ExampleField(name='patron_id', value=1, summary='Patron ID')]),
    ],
)
def get_patron(
    patron_id: t.Annotated[str, tp.Summary('Unique patron identifier'), tp.Required()],
) -> t.Annotated[Patron, tp.Summary('Patron information')]:
    patron_service: PatronService = current_app.container.patron_service()  # type: ignore
    return patron_service.get_patron(patron_id)


@jsonrpc_bp.method(
    'Patrons.create',
    tm.MethodAnnotated[
        tm.Summary('Create a new patron'),
        tm.Description('Register a new patron and set a 1-year membership expiration date'),
        tm.Tag(name='patron', summary='Patron Management', description='Operations related to library patrons'),
        tm.Error(code=-32001, message='Patron already exists', data={'reason': 'duplicate card number or email'}),
        tm.Example(
            name='create_patron_example',
            summary='Create new patron',
            params=[
                tm.ExampleField(
                    name='patron',
                    value={'name': 'John Doe', 'email': 'john.doe@example.com'},
                    summary='Patron data object',
                )
            ],
        ),
    ],
)
def create_patron(
    patron: t.Annotated[PatronCreate, tp.Summary('Patron information'), tp.Required()],
) -> t.Annotated[Patron, tp.Summary('Created patron information')]:
    patron_service: PatronService = current_app.container.patron_service()  # type: ignore
    return patron_service.create_patron(branch_id=patron.branch_id, name=patron.name, email=patron.email)


@jsonrpc_bp.method(
    'Patrons.update',
    tm.MethodAnnotated[
        tm.Summary('Update patron'),
        tm.Description('Partially update patron fields'),
        tm.Tag(name='patrons'),
        tm.Error(code=-32003, message='Update failed', data={'reason': 'patron not found or invalid data'}),
        tm.Example(
            name='update_patron_example',
            params=[
                tm.ExampleField(name='patron_update', value={'id': 1, 'name': 'John Smith'}, summary='Fields to update')
            ],
        ),
    ],
)
def update_patron(
    patron: t.Annotated[PatronUpdate, tp.Summary('Fields to update'), tp.Required()],
) -> t.Annotated[Patron, tp.Summary('Updated patron information')]:
    patron_service: PatronService = current_app.container.patron_service()  # type: ignore
    return patron_service.update_patron(patron_id=patron.id, name=patron.name)


@jsonrpc_bp.method(
    'Patrons.update_email',
    tm.MethodAnnotated[
        tm.Summary('Update patron'),
        tm.Description('Partially update patron fields'),
        tm.Tag(name='patrons'),
        tm.Error(code=-32003, message='Update failed', data={'reason': 'patron not found or invalid data'}),
        tm.Example(
            name='update_patron_example',
            params=[
                tm.ExampleField(name='patron_update', value={'id': 1, 'name': 'John Smith'}, summary='Fields to update')
            ],
        ),
    ],
)
def update_patron_email(
    patron_id: t.Annotated[str, tp.Summary('Unique patron identifier'), tp.Required()],
    email: t.Annotated[str, tp.Summary('Patron email address'), tp.Required()],
) -> t.Annotated[Patron, tp.Summary('Updated patron information')]:
    patron_service: PatronService = current_app.container.patron_service()  # type: ignore
    return patron_service.update_patron_email(patron_id=patron_id, email=email)


@jsonrpc_bp.method(
    'Patrons.activate',
    tm.MethodAnnotated[
        tm.Summary('Delete patron'),
        tm.Description('Remove a patron record'),
        tm.Tag(name='patrons'),
        tm.Error(code=-32004, message='Deletion failed', data={'reason': 'patron not found'}),
        tm.Example(
            name='delete_patron_example', params=[tm.ExampleField(name='patron_id', value=1, summary='Patron ID')]
        ),
    ],
)
def activate_patron(
    patron_id: t.Annotated[str, tp.Summary('Patron ID'), tp.Required()],
) -> t.Annotated[Patron, tp.Summary('Updated patron information')]:
    patron_service: PatronService = current_app.container.patron_service()  # type: ignore
    return patron_service.activate_patron(patron_id)


@jsonrpc_bp.method(
    'Patrons.archive',
    tm.MethodAnnotated[
        tm.Summary('Delete patron'),
        tm.Description('Remove a patron record'),
        tm.Tag(name='patrons'),
        tm.Error(code=-32004, message='Deletion failed', data={'reason': 'patron not found'}),
        tm.Example(
            name='delete_patron_example', params=[tm.ExampleField(name='patron_id', value=1, summary='Patron ID')]
        ),
    ],
)
def archive_patron(
    patron_id: t.Annotated[str, tp.Summary('Patron ID'), tp.Required()],
) -> t.Annotated[Patron, tp.Summary('Updated patron information')]:
    patron_service: PatronService = current_app.container.patron_service()  # type: ignore
    return patron_service.archive_patron(patron_id)


@jsonrpc_bp.method(
    'Fines.list',
    tm.MethodAnnotated[
        tm.Summary('List fines'),
        tm.Description('Retrieve all fines'),
        tm.Tag(name='fine'),
        tm.Example(name='list_fines_example', params=[]),
    ],
)
def list_fines() -> t.Annotated[Page[Fine], tp.Summary('Fine list')]:
    fine_service: FineService = current_app.container.fine_service()  # type: ignore
    fines = fine_service.find_all_fines()
    return Page[Fine](results=fines, count=len(fines))


@jsonrpc_bp.method(
    'Fines.get',
    tm.MethodAnnotated[
        tm.Summary('Get patron by ID'),
        tm.Description('Retrieve patron information using unique ID'),
        tm.Tag(name='patrons'),
        tm.Error(code=-32002, message='Patron not found', data={'reason': 'invalid patron ID'}),
        tm.Example(name='get_patron_example', params=[tm.ExampleField(name='patron_id', value=1, summary='Patron ID')]),
    ],
)
def get_fine(
    fine_id: t.Annotated[str, tp.Summary('Unique fine identifier'), tp.Required()],
) -> t.Annotated[Fine, tp.Summary('Fine information')]:
    fine_service: FineService = current_app.container.fine_service()  # type: ignore
    return fine_service.get_fine(fine_id)


@jsonrpc_bp.method(
    'Fines.pay',
    tm.MethodAnnotated[
        tm.Summary('Delete patron'),
        tm.Description('Remove a patron record'),
        tm.Tag(name='patrons'),
        tm.Error(code=-32004, message='Deletion failed', data={'reason': 'patron not found'}),
        tm.Example(
            name='delete_patron_example', params=[tm.ExampleField(name='patron_id', value=1, summary='Patron ID')]
        ),
    ],
)
def pay_fine(
    fine_id: t.Annotated[str, tp.Summary('Unique fine identifier'), tp.Required()],
) -> t.Annotated[Fine, tp.Summary('Fine information')]:
    fine_service: FineService = current_app.container.fine_service()  # type: ignore
    return fine_service.pay_fine(fine_id)


@jsonrpc_bp.method(
    'Fines.waive',
    tm.MethodAnnotated[
        tm.Summary('Delete patron'),
        tm.Description('Remove a patron record'),
        tm.Tag(name='patrons'),
        tm.Error(code=-32004, message='Deletion failed', data={'reason': 'patron not found'}),
        tm.Example(
            name='delete_patron_example', params=[tm.ExampleField(name='patron_id', value=1, summary='Patron ID')]
        ),
    ],
)
def waive_fine(
    fine_id: t.Annotated[str, tp.Summary('Unique fine identifier'), tp.Required()],
) -> t.Annotated[Fine, tp.Summary('Fine information')]:
    fine_service: FineService = current_app.container.fine_service()  # type: ignore
    return fine_service.waive_fine(fine_id)
