from __future__ import annotations

from unittest.mock import MagicMock, patch

from flask import Flask

from lms.app.handlers import register


@patch('lms.app.handlers.catalogs.register_handler')
@patch('lms.app.handlers.patrons.register_handler')
@patch('lms.app.handlers.organizations.register_handler')
def test_register_calls_all_handler_registrations(
    mock_orgs_register: MagicMock, mock_patrons_register: MagicMock, mock_catalogs_register: MagicMock, app: Flask
) -> None:
    register(app)

    mock_orgs_register.assert_called_once_with(app)
    mock_patrons_register.assert_called_once_with(app)
    mock_catalogs_register.assert_called_once_with(app)


@patch('lms.app.handlers.catalogs.register_handler')
@patch('lms.app.handlers.patrons.register_handler')
@patch('lms.app.handlers.organizations.register_handler')
def test_register_calls_handlers_in_correct_order(
    mock_orgs_register: MagicMock, mock_patrons_register: MagicMock, mock_catalogs_register: MagicMock, app: Flask
) -> None:
    # Create a call tracking list
    call_order = []

    mock_orgs_register.side_effect = lambda app: call_order.append('organizations')
    mock_patrons_register.side_effect = lambda app: call_order.append('patrons')
    mock_catalogs_register.side_effect = lambda app: call_order.append('catalogs')

    register(app)

    assert call_order == ['organizations', 'patrons', 'catalogs']


@patch('lms.app.handlers.catalogs.register_handler')
@patch('lms.app.handlers.patrons.register_handler')
@patch('lms.app.handlers.organizations.register_handler')
def test_register_passes_app_to_all_handlers(
    mock_orgs_register: MagicMock, mock_patrons_register: MagicMock, mock_catalogs_register: MagicMock, app: Flask
) -> None:
    register(app)

    # Verify the same app instance was passed to all
    assert mock_orgs_register.call_args[0][0] is app
    assert mock_patrons_register.call_args[0][0] is app
    assert mock_catalogs_register.call_args[0][0] is app
