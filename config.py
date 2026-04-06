import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    DATABASE_PATH = os.environ.get('DATABASE_PATH', '/data/archivesmap.db')

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('BASE_URL', '').startswith('https')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)

    # Email (SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_DEFAULT_SENDER',
        'Archives World Map <noreply@archivesmap.org>'
    )

    # Admin (single account via .env)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH', '')

    # reCAPTCHA v3
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY', '')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '')
    RECAPTCHA_ENABLED = bool(os.environ.get('RECAPTCHA_SITE_KEY', ''))
    RECAPTCHA_THRESHOLD = float(os.environ.get('RECAPTCHA_THRESHOLD', '0.5'))

    # Email connection timeout (seconds) — prevents gunicorn worker from hanging
    MAIL_TIMEOUT = int(os.environ.get('MAIL_TIMEOUT', '15'))

    # Public base URL (used in email links)
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
