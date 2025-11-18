from __future__ import annotations

import typing as t

from flask import current_app

from flask_jsonrpc import JSONRPCBlueprint
import flask_jsonrpc.types.params as tp
import flask_jsonrpc.types.methods as tm

from lms.app.schemas import Page
from lms.app.schemas.organizations import StaffCreate, StaffUpdate, BranchCreate, BranchUpdate
from lms.app.services.organizations import StaffService, BranchService
from lms.domain.organizations.entities import Staff, Branch
from lms.domain.organizations.exceptions import (
    StaffBaseError,
    BranchBaseError,
    StaffDoesNotExistError,
    BranchDoesNotExistError,
)

jsonrpc_bp = JSONRPCBlueprint('organizations', __name__)


@jsonrpc_bp.errorhandler(BranchBaseError)
def handle_branch_base_error(ex: BranchBaseError) -> dict[str, t.Any]:
    message = ex.args[0] if ex.args else 'Unknown error'
    return {'detail': message, 'code': ex.__class__.__name__}


@jsonrpc_bp.errorhandler(BranchDoesNotExistError)
def handle_branch_does_not_exist(ex: BranchDoesNotExistError) -> dict[str, t.Any]:
    return {'detail': 'Branch does not exist', 'code': ex.__class__.__name__}


@jsonrpc_bp.method(
    'Branches.list',
    tm.MethodAnnotated[
        tm.Summary('Get all branches'),
        tm.Description('Retrieve a list of all library branches'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32002, message='No branches found', data={'reason': 'no branches available'}),
        tm.Example(name='all_branches_example', params=[]),
    ],
)
def list_branches() -> t.Annotated[Page[Branch], tp.Summary('Branch information')]:
    branch_service: BranchService = current_app.container.branch_service()  # type: ignore
    branches = branch_service.find_all_branches()
    return Page[Branch](results=branches, count=len(branches))


@jsonrpc_bp.method(
    'Branches.get',
    tm.MethodAnnotated[
        tm.Summary('Get branch by ID'),
        tm.Description('Retrieve branch information using its unique ID'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32002, message='Branch not found', data={'reason': 'invalid branch ID'}),
        tm.Example(name='get_branch_example', params=[tm.ExampleField(name='branch_id', value=1, summary='Branch ID')]),
    ],
)
def get_branch(
    branch_id: t.Annotated[str, tp.Summary('Unique branch identifier'), tp.Required()],
) -> t.Annotated[Branch, tp.Summary('Branch information')]:
    branch_service: BranchService = current_app.container.branch_service()  # type: ignore
    return branch_service.get_branch(branch_id)


@jsonrpc_bp.method(
    'Branches.create',
    tm.MethodAnnotated[
        tm.Summary('Create a new branch'),
        tm.Description('Create a new library branch with name and location details'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32001, message='Branch creation failed', data={'reason': 'duplicate name or invalid data'}),
        tm.Example(
            name='create_branch_example',
            summary='Create new branch',
            params=[
                tm.ExampleField(
                    name='branch_data',
                    value={
                        'name': 'Downtown Branch',
                        'address': '123 Main St',
                        'phone': '555-0100',
                        'email': 'downtown@lms.com',
                    },
                    summary='Branch data object',
                )
            ],
        ),
    ],
)
def create_branch(
    branch: t.Annotated[BranchCreate, tp.Summary('Branch information'), tp.Required()],
) -> t.Annotated[Branch, tp.Summary('Created branch information')]:
    branch_service: BranchService = current_app.container.branch_service()  # type: ignore
    created_branch = branch_service.create_branch(
        name=branch.name, address=branch.address, phone=branch.phone, email=branch.email, manager_id=branch.manager_id
    )
    return created_branch


@jsonrpc_bp.method(
    'Branches.update',
    tm.MethodAnnotated[
        tm.Summary('Update an existing branch'),
        tm.Description('Update an existing library branch with new details'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32001, message='Branch update failed', data={'reason': 'branch not found or invalid data'}),
        tm.Example(
            name='update_branch_example',
            summary='Update existing branch',
            params=[
                tm.ExampleField(
                    name='branch_data',
                    value={'id': 1, 'name': 'Downtown Branch', 'address': '123 Main St', 'contact_number': '555-0100'},
                    summary='Branch data object',
                )
            ],
        ),
    ],
)
def update_branch(
    branch: t.Annotated[BranchUpdate, tp.Summary('Branch information'), tp.Required()],
) -> t.Annotated[Branch, tp.Summary('Updated branch information')]:
    branch_service: BranchService = current_app.container.branch_service()  # type: ignore
    updated_branch = branch_service.update_branch(
        branch_id=branch.branch_id, name=branch.name, address=branch.address, phone=branch.phone
    )
    return updated_branch


@jsonrpc_bp.method(
    'Branches.assign_manager',
    tm.MethodAnnotated[
        tm.Summary('Assign a manager to a branch'),
        tm.Description('Assign a manager to a library branch'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32001, message='Manager assignment failed', data={'reason': 'branch or manager not found'}),
        tm.Example(
            name='assign_manager_example',
            summary='Assign manager to branch',
            params=[
                tm.ExampleField(
                    name='branch_data', value={'branch_id': 1, 'manager_id': 2}, summary='Branch and manager IDs'
                )
            ],
        ),
    ],
)
def assign_branch_manager(
    branch_id: t.Annotated[str, tp.Summary('Branch ID'), tp.Required()],
    manager_id: t.Annotated[str, tp.Summary('Manager ID'), tp.Required()],
) -> t.Annotated[Branch, tp.Summary('Updated branch information with assigned manager')]:
    branch_service: BranchService = current_app.container.branch_service()  # type: ignore
    updated_branch = branch_service.assign_branch_manager(branch_id=branch_id, manager_id=manager_id)
    return updated_branch


@jsonrpc_bp.method(
    'Branches.close',
    tm.MethodAnnotated[
        tm.Summary('Close an existing branch'),
        tm.Description('Close an existing library branch by its ID'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32001, message='Branch closing failed', data={'reason': 'branch not found or invalid data'}),
        tm.Example(
            name='delete_branch_example',
            summary='Delete existing branch',
            params=[tm.ExampleField(name='branch_data', value={'id': 1}, summary='Branch data object')],
        ),
    ],
)
def close_branch(branch_id: t.Annotated[str, tp.Summary('Branch ID'), tp.Required()]) -> None:
    branch_service: BranchService = current_app.container.branch_service()  # type: ignore
    branch_service.close_branch(branch_id=branch_id)


@jsonrpc_bp.errorhandler(StaffBaseError)
def handle_staff_base_error(ex: StaffBaseError) -> dict[str, t.Any]:
    message = ex.args[0] if ex.args else 'Unknown error'
    return {'detail': message, 'code': ex.__class__.__name__}


@jsonrpc_bp.errorhandler(StaffDoesNotExistError)
def handle_staff_does_not_exist(ex: StaffDoesNotExistError) -> dict[str, t.Any]:
    return {'detail': 'Staff does not exist', 'code': ex.__class__.__name__}


@jsonrpc_bp.method(
    'Staff.list',
    tm.MethodAnnotated[
        tm.Summary('Get all staff members'),
        tm.Description('Retrieve a list of all library staff members'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32002, message='No staff found', data={'reason': 'no staff available'}),
        tm.Example(name='all_staff_example', params=[]),
    ],
)
def list_staff() -> t.Annotated[Page[Staff], tp.Summary('List of all staff')]:
    staff_service: StaffService = current_app.container.staff_service()  # type: ignore
    staffs = staff_service.find_all_staff()
    return Page[Staff](results=staffs, count=len(staffs))


@jsonrpc_bp.method(
    'Staff.get',
    tm.MethodAnnotated[
        tm.Summary('Get staff by ID'),
        tm.Description('Retrieve staff member information using their unique ID'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32002, message='Staff not found', data={'reason': 'invalid staff ID'}),
        tm.Example(name='get_staff_example', params=[tm.ExampleField(name='staff_id', value=1, summary='Staff ID')]),
    ],
)
def get_staff(
    staff_id: t.Annotated[str, tp.Summary('Unique staff identifier'), tp.Required()],
) -> t.Annotated[Staff, tp.Summary('Staff information')]:
    staff_service: StaffService = current_app.container.staff_service()  # type: ignore
    return staff_service.get_staff(staff_id)


@jsonrpc_bp.method(
    'Staff.create',
    tm.MethodAnnotated[
        tm.Summary('Create a new staff member'),
        tm.Description('Register a new staff member with name, role, and branch assignment'),
        tm.Tag(name='staff', summary='Staff Management', description='Operations related to library staff'),
        tm.Error(code=-32001, message='Staff creation failed', data={'reason': 'duplicate email or invalid data'}),
        tm.Example(
            name='create_staff_example',
            summary='Create new staff member',
            params=[
                tm.ExampleField(
                    name='staff_data',
                    value={'name': 'Jane Smith', 'email': 'jane.smith@library.com', 'role': 'librarian'},
                    summary='Staff data object',
                )
            ],
        ),
    ],
)
def create_staff(
    staff: t.Annotated[StaffCreate, tp.Summary('Staff information'), tp.Required()],
) -> t.Annotated[Staff, tp.Summary('Created staff information')]:
    staff_service: StaffService = current_app.container.staff_service()  # type: ignore
    created_staff = staff_service.create_staff(name=staff.name, email=staff.email, role=staff.role)
    return created_staff


@jsonrpc_bp.method(
    'Staff.update',
    tm.MethodAnnotated[
        tm.Summary('Update an existing staff member'),
        tm.Description('Update an existing staff member with new details'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32001, message='Staff update failed', data={'reason': 'staff not found or invalid data'}),
        tm.Example(
            name='update_staff_example',
            summary='Update existing staff member',
            params=[
                tm.ExampleField(name='staff_id', value=1, summary='Staff ID to update'),
                tm.ExampleField(name='staff_data', value={'name': 'Jane Smith Updated'}, summary='Staff data object'),
            ],
        ),
    ],
)
def update_staff(
    staff: t.Annotated[StaffUpdate, tp.Summary('Staff information'), tp.Required()],
) -> t.Annotated[Staff, tp.Summary('Updated staff information')]:
    staff_service: StaffService = current_app.container.staff_service()  # type: ignore
    updated_staff = staff_service.update_staff(staff_id=staff.staff_id, name=staff.name)
    return updated_staff


@jsonrpc_bp.method(
    'Staff.update_email',
    tm.MethodAnnotated[
        tm.Summary('Update an existing staff member'),
        tm.Description('Update an existing staff member with new details'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32001, message='Staff update failed', data={'reason': 'staff not found or invalid data'}),
        tm.Example(
            name='update_staff_example',
            summary='Update existing staff member',
            params=[
                tm.ExampleField(name='staff_id', value=1, summary='Staff ID to update'),
                tm.ExampleField(
                    name='staff_data',
                    value={
                        'name': 'Jane Smith Updated',
                        'email': 'jane.updated@library.com',
                        'role': 'senior_librarian',
                    },
                    summary='Staff data object',
                ),
            ],
        ),
    ],
)
def update_staff_email(
    staff_id: t.Annotated[str, tp.Summary('Staff ID'), tp.Required()],
    email: t.Annotated[str, tp.Summary('New email address'), tp.Required()],
) -> t.Annotated[Staff, tp.Summary('Updated staff email information')]:
    staff_service: StaffService = current_app.container.staff_service()  # type: ignore
    updated_staff = staff_service.update_staff_email(staff_id=staff_id, email=email)
    return updated_staff


@jsonrpc_bp.method(
    'Staff.update_role',
    tm.MethodAnnotated[
        tm.Summary('Update an existing staff member'),
        tm.Description('Update an existing staff member with new details'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32001, message='Staff update failed', data={'reason': 'staff not found or invalid data'}),
        tm.Example(
            name='update_staff_example',
            summary='Update existing staff member',
            params=[
                tm.ExampleField(name='staff_id', value=1, summary='Staff ID to update'),
                tm.ExampleField(name='staff', value={'role': 'senior_librarian'}, summary='Staff data object'),
            ],
        ),
    ],
)
def update_staff_role(
    staff_id: t.Annotated[str, tp.Summary('Staff ID'), tp.Required()],
    role: t.Annotated[str, tp.Summary('New role'), tp.Required()],
) -> t.Annotated[Staff, tp.Summary('Updated staff role information')]:
    staff_service: StaffService = current_app.container.staff_service()  # type: ignore
    updated_staff = staff_service.assign_staff_role(staff_id=staff_id, role=role)
    return updated_staff


@jsonrpc_bp.method(
    'Staff.inactivate',
    tm.MethodAnnotated[
        tm.Summary('Delete an existing staff member'),
        tm.Description('Delete an existing staff member by their ID'),
        tm.Tag(name='organizations'),
        tm.Error(code=-32001, message='Staff deletion failed', data={'reason': 'staff not found or invalid data'}),
        tm.Example(
            name='delete_staff_example',
            summary='Delete existing staff member',
            params=[tm.ExampleField(name='staff_id', value=1, summary='Staff ID to delete')],
        ),
    ],
)
def inactivate_staff(
    staff_id: t.Annotated[str, tp.Summary('Staff ID'), tp.Required()],
) -> t.Annotated[Staff, tp.Summary('Updated staff role information')]:
    staff_service: StaffService = current_app.container.staff_service()  # type: ignore
    return staff_service.inactivate_staff(staff_id=staff_id)
