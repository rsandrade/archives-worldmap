import functools
import secrets
import string

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, current_app, flash,
)
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db
from ..email_utils import send_approved_email, send_rejected_email

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return wrapped


@admin_bp.route('/login', methods=['GET'])
def login():
    if session.get('admin_logged'):
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html')


@admin_bp.route('/login', methods=['POST'])
def login_submit():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    expected_user = current_app.config['ADMIN_USERNAME']
    expected_hash = current_app.config['ADMIN_PASSWORD_HASH']

    # Check permanent password from .env
    if username == expected_user and expected_hash and check_password_hash(expected_hash, password):
        session['admin_logged'] = True
        return redirect(url_for('admin.dashboard'))

    # Check temporary reset password from DB
    if username == expected_user:
        db = get_db()
        reset = db.execute(
            "SELECT id, hash FROM password_resets WHERE expires_at > datetime('now') ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if reset and check_password_hash(reset['hash'], password):
            db.execute('DELETE FROM password_resets WHERE id = ?', (reset['id'],))
            db.commit()
            session['admin_logged'] = True
            flash('Logged in with temporary password. Please update your ADMIN_PASSWORD_HASH.', 'warning')
            return redirect(url_for('admin.dashboard'))

    flash('Invalid credentials.', 'danger')
    return redirect(url_for('admin.login'))


@admin_bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('admin/forgot_password.html')


@admin_bp.route('/forgot-password', methods=['POST'])
def forgot_password_submit():
    admin_email = current_app.config.get('ADMIN_EMAIL', '')
    if not admin_email:
        flash('ADMIN_EMAIL is not configured.', 'danger')
        return redirect(url_for('admin.forgot_password'))

    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    new_password = ''.join(secrets.choice(alphabet) for _ in range(20))
    hashed = generate_password_hash(new_password)

    db = get_db()
    db.execute('DELETE FROM password_resets')  # only one reset at a time
    db.execute(
        "INSERT INTO password_resets (hash, expires_at) VALUES (?, datetime('now', '+1 hour'))",
        (hashed,),
    )
    db.commit()

    from ..email_utils import send_password_reset_email
    send_password_reset_email(new_password)

    flash('A temporary password has been sent to the admin email.', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('public.home'))


@admin_bp.route('/')
@admin_required
def dashboard():
    db = get_db()
    status_filter = request.args.get('status', 'waiting')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    if status_filter == 'all':
        rows = db.execute(
            'SELECT * FROM institutions ORDER BY submitted_at DESC LIMIT ? OFFSET ?',
            (per_page, offset),
        ).fetchall()
        total = db.execute('SELECT COUNT(*) AS c FROM institutions').fetchone()['c']
    else:
        rows = db.execute(
            'SELECT * FROM institutions WHERE status = ? ORDER BY submitted_at DESC LIMIT ? OFFSET ?',
            (status_filter, per_page, offset),
        ).fetchall()
        total = db.execute(
            'SELECT COUNT(*) AS c FROM institutions WHERE status = ?', (status_filter,)
        ).fetchone()['c']

    counts = {
        'waiting': db.execute("SELECT COUNT(*) AS c FROM institutions WHERE status='waiting'").fetchone()['c'],
        'verified': db.execute("SELECT COUNT(*) AS c FROM institutions WHERE status='verified'").fetchone()['c'],
        'rejected': db.execute("SELECT COUNT(*) AS c FROM institutions WHERE status='rejected'").fetchone()['c'],
    }

    return render_template(
        'admin/dashboard.html',
        institutions=rows, total=total, counts=counts,
        status_filter=status_filter, page=page, per_page=per_page,
    )


@admin_bp.route('/approve/<int:inst_id>')
@admin_required
def approve(inst_id):
    db = get_db()
    db.execute(
        "UPDATE institutions SET status='verified', moderated_at=datetime('now') WHERE id=?",
        (inst_id,),
    )
    db.commit()

    inst = db.execute('SELECT * FROM institutions WHERE id=?', (inst_id,)).fetchone()
    if inst:
        send_approved_email(dict(inst))

    flash(f'Institution approved.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/reject/<int:inst_id>')
@admin_required
def reject(inst_id):
    db = get_db()
    db.execute(
        "UPDATE institutions SET status='rejected', moderated_at=datetime('now') WHERE id=?",
        (inst_id,),
    )
    db.commit()

    inst = db.execute('SELECT * FROM institutions WHERE id=?', (inst_id,)).fetchone()
    if inst:
        send_rejected_email(dict(inst))

    flash(f'Institution rejected.', 'info')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/edit/<int:inst_id>', methods=['GET'])
@admin_required
def edit(inst_id):
    db = get_db()
    inst = db.execute('SELECT * FROM institutions WHERE id=?', (inst_id,)).fetchone()
    if not inst:
        flash('Institution not found.', 'warning')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit.html', institution=inst)


@admin_bp.route('/edit/<int:inst_id>', methods=['POST'])
@admin_required
def edit_submit(inst_id):
    db = get_db()
    db.execute(
        '''UPDATE institutions SET
           name=?, latitude=?, longitude=?, address=?, city=?, district=?,
           country=?, url=?, email=?, identifier=?, admin_notes=?
           WHERE id=?''',
        (
            request.form['name'],
            request.form['latitude'],
            request.form['longitude'],
            request.form.get('address', ''),
            request.form.get('city', ''),
            request.form.get('district', ''),
            request.form.get('country', ''),
            request.form.get('url', ''),
            request.form.get('email', ''),
            request.form.get('identifier', ''),
            request.form.get('admin_notes', ''),
            inst_id,
        ),
    )
    db.commit()
    flash('Institution updated.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete/<int:inst_id>')
@admin_required
def delete(inst_id):
    db = get_db()
    db.execute('DELETE FROM institutions WHERE id=?', (inst_id,))
    db.commit()
    flash('Institution deleted.', 'info')
    return redirect(url_for('admin.dashboard'))
