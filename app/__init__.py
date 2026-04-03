import os
import sqlite3

from flask import Flask
from .extensions import mail


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    mail.init_app(app)
    _init_db(app)

    from .routes.public import public_bp
    from .routes.moderation import moderation_bp
    from .routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(moderation_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from .db import close_db
    app.teardown_appcontext(close_db)

    @app.context_processor
    def inject_globals():
        return {
            'recaptcha_site_key': app.config['RECAPTCHA_SITE_KEY'],
            'recaptcha_enabled': app.config['RECAPTCHA_ENABLED'],
        }

    return app


def _init_db(app):
    db_path = app.config['DATABASE_PATH']
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'schema.sql')
    with sqlite3.connect(db_path) as conn:
        with open(schema_path) as f:
            conn.executescript(f.read())
