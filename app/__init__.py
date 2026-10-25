from pathlib import Path

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_folder='static')
    app.config.from_mapping(
        DATABASE=str(Path(__file__).resolve().parent.parent / 'feedy.db'),
        SECRET_KEY='feedy-dev-secret-key',
    )

    if test_config is not None:
        app.config.update(test_config)

    from app import database
    app.teardown_appcontext(database.close_db)

    with app.app_context():
        database.init_db()

    from app.routes import init_app
    init_app(app)

    return app
