from __future__ import annotations

import typing as t

from flask import current_app

from flask_jsonrpc import JSONRPCBlueprint
import flask_jsonrpc.types.params as tp
import flask_jsonrpc.types.methods as tm

from lms.app.schemas import Page
from lms.app.schemas.catalogs import ItemCreate, ItemUpdate
from lms.app.services.catalogs import CopyService, ItemService
from lms.domain.catalogs.entities import Copy, Item

jsonrpc_bp = JSONRPCBlueprint('catalogs', __name__)


@jsonrpc_bp.method(
    'Copies.list',
    tm.MethodAnnotated[
        tm.Summary('Get all catalog copies'),
        tm.Description('Retrieve a list of all copies in the library catalog'),
        tm.Tag(name='catalogs'),
        tm.Error(code=-32002, message='No copies found', data={'reason': 'no catalog copies available'}),
        tm.Example(name='all_catalog_copies_example', params=[]),
    ],
)
def list_copies() -> t.Annotated[Page[Copy], tp.Summary('Catalog copies search result')]:
    copy_service: CopyService = current_app.container.copy_service()  # type: ignore
    items = copy_service.get_all_copies()
    return Page[Copy](results=items, count=len(items))


@jsonrpc_bp.method(
    'Copies.get',
    tm.MethodAnnotated[
        tm.Summary('Get copy by ID'),
        tm.Description('Retrieve physical copy information using its unique ID'),
        tm.Tag(name='catalogs'),
        tm.Error(code=-32002, message='Copy not found', data={'reason': 'invalid copy ID'}),
        tm.Example(name='get_copy_example', params=[tm.ExampleField(name='copy_id', value=1, summary='Copy ID')]),
    ],
)
def get_copy(
    copy_id: t.Annotated[str, tp.Summary('Copy ID'), tp.Required()],
) -> t.Annotated[Copy, tp.Summary('Copy information')]:
    copy_service: CopyService = current_app.container.copy_service()  # type: ignore
    return copy_service.get_copy(copy_id)


@jsonrpc_bp.method(
    'Items.list',
    tm.MethodAnnotated[
        tm.Summary('Get all catalog items'),
        tm.Description('Retrieve a list of all items in the library catalog'),
        tm.Tag(name='catalogs'),
        tm.Error(code=-32002, message='No items found', data={'reason': 'no catalog items available'}),
        tm.Example(name='all_catalog_items_example', params=[]),
    ],
)
def list_items() -> t.Annotated[Page[Item], tp.Summary('Catalog items search result')]:
    item_service: ItemService = current_app.container.item_service()  # type: ignore
    items = item_service.get_all_items()
    return Page[Item](results=items, count=len(items))


@jsonrpc_bp.method(
    'Items.create',
    tm.MethodAnnotated[
        tm.Summary('Create a new catalog item'),
        tm.Description('Add a new item to the library catalog with title, barcode and material type'),
        tm.Tag(name='catalogs'),
        tm.Error(code=-32001, message='Item creation failed', data={'reason': 'duplicate barcode or invalid data'}),
        tm.Example(
            name='create_catalog_item_example',
            summary='Create new catalog item',
            params=[
                tm.ExampleField(
                    name='item_data',
                    value={
                        'barcode': 'BK-0001',
                        'title': 'The Pragmatic Programmer',
                        'author': 'Andrew Hunt',
                        'material_type': 'book',
                    },
                    summary='Item data object',
                )
            ],
        ),
    ],
)
def create_item(
    item: t.Annotated[ItemCreate, tp.Summary('Item information'), tp.Required()],
) -> t.Annotated[Item, tp.Summary('Created catalog item')]:
    item_service: ItemService = current_app.container.item_service()  # type: ignore
    return item_service.create_item(
        title=item.title,
        isbn=item.isbn,
        publisher_id=item.publisher_id,
        publication_year=item.publication_year,
        category_id=item.category_id,
        edition=item.edition,
        format=item.format,
        description=item.description,
    )


@jsonrpc_bp.method(
    'Items.get',
    tm.MethodAnnotated[
        tm.Summary('Get catalog item by ID'),
        tm.Description('Retrieve catalog item information using its unique ID'),
        tm.Tag(name='catalogs'),
        tm.Error(code=-32002, message='Item not found', data={'reason': 'invalid item ID'}),
        tm.Example(
            name='get_catalog_item_example', params=[tm.ExampleField(name='item_id', value=1, summary='Item ID')]
        ),
    ],
)
def get_item(
    item_id: t.Annotated[str, tp.Summary('Item ID'), tp.Required()],
) -> t.Annotated[Item, tp.Summary('Catalog item information')]:
    item_service: ItemService = current_app.container.item_service()  # type: ignore
    return item_service.get_item(item_id)


@jsonrpc_bp.method(
    'Items.update',
    tm.MethodAnnotated[
        tm.Summary('Update catalog item'),
        tm.Description('Update an existing catalog item with new metadata'),
        tm.Tag(name='catalogs'),
        tm.Error(code=-32001, message='Item update failed', data={'reason': 'item not found or invalid data'}),
        tm.Example(
            name='update_catalog_item_example',
            summary='Update existing catalog item',
            params=[
                tm.ExampleField(name='item_id', value=1, summary='Item ID to update'),
                tm.ExampleField(
                    name='item_data',
                    value={'title': 'Pragmatic Programmer 2nd Ed', 'isbn': '978-0135957059'},
                    summary='Partial item data object',
                ),
            ],
        ),
    ],
)
def update_item(
    item: t.Annotated[ItemUpdate, tp.Summary('Item update information'), tp.Required()],
) -> t.Annotated[Item, tp.Summary('Updated catalog item')]:
    item_service: ItemService = current_app.container.item_service()  # type: ignore
    return item_service.update_item(item_id=item.id, title=item.title, isbn=item.isbn, description=item.description)
