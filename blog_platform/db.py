import sqlite3

import click
from flask import current_app, g


def get_db():
    """Return a SQLite connection for the current app/request context.

    In testing mode a single persistent shared in-memory connection is
    reused so that the schema and data survive across requests within a
    test. In normal mode a fresh connection is opened per request and
    closed on teardown, as recommended by Flask.
    """
    if "db" not in g:
        if current_app.config.get("TESTING"):
            g.db = current_app.config["_TEST_DB_CONN"]
        else:
            g.db = sqlite3.connect(
                current_app.config["DATABASE"],
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None and not current_app.config.get("TESTING"):
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    if app.config.get("TESTING"):
        # A single, shared, in-memory SQLite database kept alive for the
        # lifetime of the app so table state persists across requests.
        conn = sqlite3.connect(
            app.config["DATABASE"], uri=True, check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        app.config["_TEST_DB_CONN"] = conn
        with app.app_context():
            init_db()

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
