from __future__ import annotations

import typing as t

from flask import current_app

from flask_jsonrpc import JSONRPCBlueprint
import flask_jsonrpc.types.params as tp
import flask_jsonrpc.types.methods as tm

from lms.app.schemas import Page
from lms.app.services.circulations import HoldService, LoanService
from lms.domain.circulations.entities import Hold, Loan

jsonrpc_bp = JSONRPCBlueprint('circulation', __name__)


@jsonrpc_bp.method(
    'Loan.list',
    tm.MethodAnnotated[
        tm.Summary('Get all loans'),
        tm.Description('Retrieve a list of all active and returned loans'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32002, message='No loans found', data={'reason': 'no loans available'}),
        tm.Example(name='all_loans_example', params=[]),
    ],
)
def list_loans() -> t.Annotated[Page[Loan], tp.Summary('Loan search result')]:
    loan_service: LoanService = current_app.container.loan_service()  # type: ignore
    loans = loan_service.find_all_loans()
    return Page[Loan](results=loans, count=len(loans))


@jsonrpc_bp.method(
    'Loan.checkout_copy',
    tm.MethodAnnotated[
        tm.Summary('Check out a copy to a patron'),
        tm.Description('Check out a copy (treated as item_id in request) to a patron'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32001, message='Loan creation failed', data={'reason': 'invalid patron or copy'}),
        tm.Example(
            name='create_loan_example',
            params=[
                tm.ExampleField(
                    name='loan_data',
                    value={'patron_id': 10, 'item_id': 200, 'due_date': '2025-11-30'},
                    summary='Loan data object',
                )
            ],
        ),
    ],
)
def checkout_copy(
    patron_id: t.Annotated[str, tp.Summary('Patron ID'), tp.Required()],
    copy_id: t.Annotated[str, tp.Summary('Copy ID'), tp.Required()],
    staff_id: t.Annotated[str, tp.Summary('Staff ID'), tp.Required()],
) -> t.Annotated[Loan, tp.Summary('Created loan')]:
    loan_service: LoanService = current_app.container.loan_service()  # type: ignore
    return loan_service.checkout_copy(copy_id=copy_id, patron_id=patron_id, staff_out_id=staff_id)


@jsonrpc_bp.method(
    'Loan.checkin_copy',
    tm.MethodAnnotated[
        tm.Summary('Check in a copy from a patron'),
        tm.Description('Check in a copy (treated as item_id in request) from a patron'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32001, message='Loan check-in failed', data={'reason': 'invalid patron or copy'}),
        tm.Example(
            name='create_loan_example',
            params=[
                tm.ExampleField(
                    name='loan_data',
                    value={'patron_id': 10, 'item_id': 200, 'due_date': '2025-11-30'},
                    summary='Loan data object',
                )
            ],
        ),
    ],
)
def checkin_copy(
    loan_id: t.Annotated[str, tp.Summary('Loan ID'), tp.Required()],
    staff_id: t.Annotated[str, tp.Summary('Staff ID'), tp.Required()],
) -> t.Annotated[Loan, tp.Summary('Created loan')]:
    loan_service: LoanService = current_app.container.loan_service()  # type: ignore
    return loan_service.checkin_copy(loan_id=loan_id, staff_in_id=staff_id)


@jsonrpc_bp.method(
    'Loan.damaged_copy',
    tm.MethodAnnotated[
        tm.Summary('Update loan'),
        tm.Description('Partially update loan fields (due_date, staff assignments, fine_amount)'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32001, message='Loan update failed', data={'reason': 'loan not found or invalid data'}),
        tm.Example(
            name='update_loan_example',
            params=[
                tm.ExampleField(name='loan_id', value=1, summary='Loan ID'),
                tm.ExampleField(name='due_date', value='2025-12-01', summary='New due date'),
            ],
        ),
    ],
)
def damaged_copy(
    loan_id: t.Annotated[str, tp.Summary('Loan ID'), tp.Required()],
) -> t.Annotated[Loan, tp.Summary('Updated loan information')]:
    loan_service: LoanService = current_app.container.loan_service()  # type: ignore
    return loan_service.damaged_copy(loan_id)


@jsonrpc_bp.method(
    'Loan.lost_copy',
    tm.MethodAnnotated[
        tm.Summary('Update loan'),
        tm.Description('Partially update loan fields (due_date, staff assignments, fine_amount)'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32001, message='Loan update failed', data={'reason': 'loan not found or invalid data'}),
        tm.Example(
            name='update_loan_example',
            params=[
                tm.ExampleField(name='loan_id', value=1, summary='Loan ID'),
                tm.ExampleField(name='due_date', value='2025-12-01', summary='New due date'),
            ],
        ),
    ],
)
def lost_copy(
    loan_id: t.Annotated[str, tp.Summary('Loan ID'), tp.Required()],
) -> t.Annotated[Loan, tp.Summary('Updated loan information')]:
    loan_service: LoanService = current_app.container.loan_service()  # type: ignore
    return loan_service.lost_copy(loan_id)


@jsonrpc_bp.method(
    'Loan.get',
    tm.MethodAnnotated[
        tm.Summary('Get loan by ID'),
        tm.Description('Retrieve loan information using its unique ID'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32002, message='Loan not found', data={'reason': 'invalid loan ID'}),
        tm.Example(name='get_loan_example', params=[tm.ExampleField(name='loan_id', value=1, summary='Loan ID')]),
    ],
)
def get_loan(
    loan_id: t.Annotated[str, tp.Summary('Loan ID'), tp.Required()],
) -> t.Annotated[Loan, tp.Summary('Loan information')]:
    loan_service: LoanService = current_app.container.loan_service()  # type: ignore
    return loan_service.get_loan(loan_id)


@jsonrpc_bp.method(
    'Loan.renew',
    tm.MethodAnnotated[
        tm.Summary('Update loan'),
        tm.Description('Partially update loan fields (due_date, staff assignments, fine_amount)'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32001, message='Loan update failed', data={'reason': 'loan not found or invalid data'}),
        tm.Example(
            name='update_loan_example',
            params=[
                tm.ExampleField(name='loan_id', value=1, summary='Loan ID'),
                tm.ExampleField(name='due_date', value='2025-12-01', summary='New due date'),
            ],
        ),
    ],
)
def renew_loan(
    loan_id: t.Annotated[str, tp.Summary('Loan ID'), tp.Required()],
) -> t.Annotated[Loan, tp.Summary('Updated loan information')]:
    loan_service: LoanService = current_app.container.loan_service()  # type: ignore
    return loan_service.renew_loan(loan_id)


@jsonrpc_bp.method(
    'Hold.list',
    tm.MethodAnnotated[
        tm.Summary('Get all holds'),
        tm.Description('Retrieve a list of all holds/reservations'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32002, message='No holds found', data={'reason': 'no holds available'}),
        tm.Example(name='all_holds_example', params=[]),
    ],
)
def list_holds() -> t.Annotated[Page[Hold], tp.Summary('Hold list')]:
    hold_service: HoldService = current_app.container.hold_service()  # type: ignore
    holds = hold_service.find_all_holds()
    return Page[Hold](results=holds, count=len(holds))


@jsonrpc_bp.method(
    'Hold.get',
    tm.MethodAnnotated[
        tm.Summary('Get hold by ID'),
        tm.Description('Retrieve hold information using its unique ID'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32002, message='Hold not found', data={'reason': 'invalid hold ID'}),
        tm.Example(name='get_hold_example', params=[tm.ExampleField(name='hold_id', value=1, summary='Hold ID')]),
    ],
)
def get_hold(
    hold_id: t.Annotated[str, tp.Summary('Hold ID'), tp.Required()],
) -> t.Annotated[Hold, tp.Summary('Hold information')]:
    hold_service: HoldService = current_app.container.hold_service()  # type: ignore
    return hold_service.get_hold(hold_id)


@jsonrpc_bp.method(
    'Hold.place',
    tm.MethodAnnotated[
        tm.Summary('Create a new hold'),
        tm.Description('Place a hold on an item for a patron'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32001, message='Hold creation failed', data={'reason': 'invalid patron or item'}),
        tm.Example(
            name='create_hold_example',
            params=[
                tm.ExampleField(
                    name='hold_data',
                    value={'patron_id': 10, 'item_id': 200, 'expiry_date': '2025-12-05'},
                    summary='Hold data object',
                )
            ],
        ),
    ],
)
def place_hold(
    patron_id: t.Annotated[str, tp.Summary('Patron ID'), tp.Required()],
    item_id: t.Annotated[str, tp.Summary('Item ID'), tp.Required()],
    copy_id: t.Annotated[str | None, tp.Summary('Copy ID')] = None,
) -> t.Annotated[Hold, tp.Summary('Created hold')]:
    hold_service: HoldService = current_app.container.hold_service()  # type: ignore
    return hold_service.place_hold(item_id=item_id, patron_id=patron_id, copy_id=copy_id)


@jsonrpc_bp.method(
    'Hold.pickup',
    tm.MethodAnnotated[
        tm.Summary('Create a new hold'),
        tm.Description('Place a hold on an item for a patron'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32001, message='Hold creation failed', data={'reason': 'invalid patron or item'}),
        tm.Example(
            name='create_hold_example',
            params=[
                tm.ExampleField(
                    name='hold_data',
                    value={'patron_id': 10, 'item_id': 200, 'expiry_date': '2025-12-05'},
                    summary='Hold data object',
                )
            ],
        ),
    ],
)
def pickup_hold(
    hold_id: t.Annotated[str, tp.Summary('Hold ID'), tp.Required()],
    staff_id: t.Annotated[str, tp.Summary('Staff ID'), tp.Required()],
    copy_id: t.Annotated[str, tp.Summary('Copy ID'), tp.Required()],
) -> t.Annotated[Loan, tp.Summary('Created hold')]:
    hold_service: HoldService = current_app.container.hold_service()  # type: ignore
    return hold_service.pickup_hold(hold_id=hold_id, staff_out_id=staff_id, copy_id=copy_id)


@jsonrpc_bp.method(
    'Hold.cancel',
    tm.MethodAnnotated[
        tm.Summary('Create a new hold'),
        tm.Description('Place a hold on an item for a patron'),
        tm.Tag(name='circulation'),
        tm.Error(code=-32001, message='Hold creation failed', data={'reason': 'invalid patron or item'}),
        tm.Example(
            name='create_hold_example',
            params=[
                tm.ExampleField(
                    name='hold_data',
                    value={'patron_id': 10, 'item_id': 200, 'expiry_date': '2025-12-05'},
                    summary='Hold data object',
                )
            ],
        ),
    ],
)
def cancel_hold(
    hold_id: t.Annotated[str, tp.Summary('Hold ID'), tp.Required()],
) -> t.Annotated[Hold, tp.Summary('Created hold')]:
    hold_service: HoldService = current_app.container.hold_service()  # type: ignore
    return hold_service.cancel_hold(hold_id=hold_id)
