import os
import sqlite3

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from .extensions import mail

limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    mail.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
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

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

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
