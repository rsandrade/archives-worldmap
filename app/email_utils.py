from flask import render_template, current_app
from flask_mail import Message
from .extensions import mail


def send_new_submission_email(institution: dict):
    """Notify admin with approve/reject links."""
    admin_email = current_app.config['ADMIN_EMAIL']
    if not admin_email:
        return

    base_url = current_app.config['BASE_URL'].rstrip('/')
    approve_url = f"{base_url}/approve/{institution['token']}"
    reject_url = f"{base_url}/reject/{institution['token']}"

    msg = Message(
        subject=f"[Archives World Map] New submission: {institution['name']}",
        recipients=[admin_email],
        html=render_template(
            'emails/new_submission.html',
            institution=institution,
            approve_url=approve_url,
            reject_url=reject_url,
        ),
    )
    mail.send(msg)


def send_approved_email(institution: dict):
    """Notify contributor that submission was approved."""
    if not institution.get('collaborator_email'):
        return
    msg = Message(
        subject='[Archives World Map] Your submission was approved!',
        recipients=[institution['collaborator_email']],
        html=render_template('emails/approved.html', institution=institution),
    )
    mail.send(msg)


def send_rejected_email(institution: dict):
    """Notify contributor that submission was rejected."""
    if not institution.get('collaborator_email'):
        return
    msg = Message(
        subject='[Archives World Map] Regarding your submission',
        recipients=[institution['collaborator_email']],
        html=render_template('emails/rejected.html', institution=institution),
    )
    mail.send(msg)


def send_report_email(institution: dict, reporter_email: str, reason: str):
    """Forward a report about an incorrect/fake institution to admin."""
    admin_email = current_app.config['ADMIN_EMAIL']
    if not admin_email:
        return
    msg = Message(
        subject=f"[Archives World Map] Report: {institution['name']}",
        recipients=[admin_email],
        reply_to=reporter_email or None,
        html=render_template(
            'emails/report.html',
            institution=institution,
            reporter_email=reporter_email,
            reason=reason,
        ),
    )
    mail.send(msg)


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
            f'After logging in, generate a permanent hash with:\n'
            f'  docker compose exec web flask hash-password <new-password>\n'
            f'and update ADMIN_PASSWORD_HASH in your .env file.'
        ),
    )
    mail.send(msg)


def send_contact_email(name: str, email: str, institution: str, subject: str, body: str):
    """Forward contact form to admin."""
    admin_email = current_app.config['ADMIN_EMAIL']
    if not admin_email:
        return
    msg = Message(
        subject=f'[Archives World Map] {subject}',
        recipients=[admin_email],
        reply_to=email,
        html=render_template(
            'emails/contact.html',
            name=name, email=email, institution=institution, body=body,
        ),
    )
    mail.send(msg)
