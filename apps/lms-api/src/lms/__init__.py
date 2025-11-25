from __future__ import annotations

import click

from .app import create_app

app = create_app()


@app.cli.command('db-init')
def db_init_command() -> None:
    with app.app_context():
        from lms.infrastructure.database.db import init_db

        init_db(app)
    click.echo('Database initialized.')
