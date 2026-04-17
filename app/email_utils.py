import logging
import re
import threading

from flask import render_template, current_app
from flask_mail import Message
from .extensions import mail

logger = logging.getLogger(__name__)


def _clean_header(value):
    """Remove newlines and control characters from email header values."""
    return re.sub(r'[\r\n\x00]', '', str(value)).strip()[:255]


def _send_async(app, msg):
    """Send a Flask-Mail message in a background thread."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            logger.error("Failed to send email to %s: %s", msg.recipients, e)


def _send(msg):
    """Dispatch email asynchronously so the HTTP request is never blocked."""
    app = current_app._get_current_object()
    t = threading.Thread(target=_send_async, args=(app, msg), daemon=True)
    t.start()


def send_new_submission_email(institution: dict):
    """Notify admin with approve/reject links."""
    admin_email = current_app.config['ADMIN_EMAIL']
    if not admin_email:
        return

    base_url = current_app.config['BASE_URL'].rstrip('/')
    approve_url = f"{base_url}/approve/{institution['token']}"
    reject_url = f"{base_url}/reject/{institution['token']}"

    msg = Message(
        subject=f"[Archives World Map] New submission: {_clean_header(institution['name'])}",
        recipients=[admin_email],
        html=render_template(
            'emails/new_submission.html',
            institution=institution,
            approve_url=approve_url,
            reject_url=reject_url,
        ),
    )
    _send(msg)


def send_approved_email(institution: dict):
    """Notify contributor that submission was approved."""
    if not institution.get('collaborator_email'):
        return
    msg = Message(
        subject='[Archives World Map] Your submission was approved!',
        recipients=[institution['collaborator_email']],
        html=render_template('emails/approved.html', institution=institution),
    )
    _send(msg)


def send_rejected_email(institution: dict):
    """Notify contributor that submission was rejected."""
    if not institution.get('collaborator_email'):
        return
    msg = Message(
        subject='[Archives World Map] Regarding your submission',
        recipients=[institution['collaborator_email']],
        html=render_template('emails/rejected.html', institution=institution),
    )
    _send(msg)


def send_report_email(institution: dict, reporter_email: str, reason: str):
    """Forward a report about an incorrect/fake institution to admin."""
    admin_email = current_app.config['ADMIN_EMAIL']
    if not admin_email:
        return
    msg = Message(
        subject=f"[Archives World Map] Report: {_clean_header(institution['name'])}",
        recipients=[admin_email],
        reply_to=_clean_header(reporter_email) or None,
        html=render_template(
            'emails/report.html',
            institution=institution,
            reporter_email=reporter_email,
            reason=reason,
        ),
    )
    _send(msg)


def send_password_reset_email(new_password: str):
    """Send temporary admin password to ADMIN_EMAIL."""
    admin_email = current_app.config['ADMIN_EMAIL']
    if not admin_email:
        return
    msg = Message(
        subject='[Archives World Map] Admin password reset',
        recipients=[admin_email],
        body=(
            f'Your temporary admin password (valid for 1 hour):\n\n'
            f'    {new_password}\n\n'
            f'Log in at: {current_app.config["BASE_URL"]}/admin/login\n\n'
            f'After logging in, go to Change Password to set a permanent password.'
        ),
    )
    _send(msg)


def send_staff_account_email(username: str, email: str, temp_password: str, is_new: bool = True):
    """Send temporary password to a new or existing staff user."""
    action = 'created' if is_new else 'reset'
    msg = Message(
        subject=f'[Archives World Map] Your account password has been {action}',
        recipients=[email],
        body=(
            f'Hello {username},\n\n'
            f'{"Your account has been created." if is_new else "Your password has been reset."}\n\n'
            f'Temporary password (valid until you change it):\n\n'
            f'    {temp_password}\n\n'
            f'Log in at: {current_app.config["BASE_URL"]}/admin/login\n\n'
            f'You will be required to set a new password after logging in.'
        ),
    )
    _send(msg)


def send_contact_email(name: str, email: str, institution: str, subject: str, body: str):
    """Forward contact form to admin."""
    admin_email = current_app.config['ADMIN_EMAIL']
    if not admin_email:
        return
    msg = Message(
        subject=f'[Archives World Map] {_clean_header(subject)}',
        recipients=[admin_email],
        reply_to=_clean_header(email),
        html=render_template(
            'emails/contact.html',
            name=name, email=email, institution=institution, body=body,
        ),
    )
    _send(msg)
