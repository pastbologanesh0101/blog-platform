import os

from flask import Flask


def create_app(test_config=None, testing=False):
    """Application factory for the Blogging Platform.

    Pass ``testing=True`` (or a ``test_config`` dict containing
    ``{"TESTING": True}``) to run against an in-memory SQLite database,
    which is ideal for unit tests.
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "blog.sqlite"),
        TESTING=testing,
    )

    if test_config:
        app.config.from_mapping(test_config)

    if app.config["TESTING"]:
        # Use a private, in-memory SQLite database for tests so that
        # nothing touches the filesystem and every test starts clean.
        app.config["DATABASE"] = "file::memory:?cache=shared"
    else:
        # Make sure the instance folder exists for the real SQLite file.
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

    from . import db
    db.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    return app
