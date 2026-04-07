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
from .. import limiter

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged'):
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return wrapped


@admin_bp.route('/login', methods=['GET'])
def login():
    return redirect(url_for('admin.dashboard'))


def _get_active_hash(db):
    """Return current password hash: DB settings override takes precedence over .env."""
    row = db.execute("SELECT value FROM settings WHERE key = 'admin_password_hash'").fetchone()
    if row:
        return row['value']
    return current_app.config['ADMIN_PASSWORD_HASH']


@admin_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login_submit():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    expected_user = current_app.config['ADMIN_USERNAME']
    db = get_db()

    # Check permanent password (DB override or .env)
    active_hash = _get_active_hash(db)
    if username == expected_user and active_hash and check_password_hash(active_hash, password):
        session.clear()
        session['admin_logged'] = True
        session.permanent = True
        return redirect(url_for('admin.dashboard'))

    # Check temporary reset password from DB
    if username == expected_user:
        reset = db.execute(
            "SELECT id, hash FROM password_resets WHERE expires_at > datetime('now') ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if reset and check_password_hash(reset['hash'], password):
            db.execute('DELETE FROM password_resets WHERE id = ?', (reset['id'],))
            db.commit()
            session.clear()
            session['admin_logged'] = True
            session['must_change_password'] = True
            session.permanent = True
            flash('Logged in with temporary password. Please set a permanent password.', 'warning')
            return redirect(url_for('admin.change_password'))

    flash('Invalid credentials.', 'danger')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('admin/forgot_password.html')


@admin_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
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
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/change-password', methods=['GET'])
@admin_required
def change_password():
    return render_template('admin/change_password.html')


@admin_bp.route('/change-password', methods=['POST'])
@admin_required
def change_password_submit():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm = request.form.get('confirm_password', '')
    from_reset = session.get('must_change_password', False)

    # Skip current password check when coming from a temporary reset login
    if not from_reset:
        db = get_db()
        active_hash = _get_active_hash(db)
        if not active_hash or not check_password_hash(active_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('admin.change_password'))

    if len(new_password) < 8:
        flash('New password must be at least 8 characters.', 'danger')
        return redirect(url_for('admin.change_password'))

    if new_password != confirm:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('admin.change_password'))

    db = get_db()
    new_hash = generate_password_hash(new_password)
    db.execute(
        "INSERT INTO settings (key, value) VALUES ('admin_password_hash', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (new_hash,),
    )
    db.commit()
    session.pop('must_change_password', None)

    flash('Password updated successfully.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('public.home'))


@admin_bp.route('/')
def dashboard():
    if not session.get('admin_logged'):
        return render_template('admin/login.html')
    db = get_db()
    status_filter = request.args.get('status', 'waiting')
    q = request.args.get('q', '').strip()[:200]
    try:
        page = max(int(request.args.get('page', 1)), 1)
    except (ValueError, TypeError):
        page = 1
    per_page = 20
    offset = (page - 1) * per_page

    like = f'%{q}%'
    search_clause = (
        " AND (name LIKE ? OR city LIKE ? OR collaborator_name LIKE ? OR collaborator_email LIKE ?)"
        if q else ""
    )
    search_params = (like, like, like, like) if q else ()

    if status_filter == 'all':
        rows = db.execute(
            f'SELECT * FROM institutions WHERE 1=1{search_clause} ORDER BY submitted_at DESC LIMIT ? OFFSET ?',
            (*search_params, per_page, offset),
        ).fetchall()
        total = db.execute(
            f'SELECT COUNT(*) AS c FROM institutions WHERE 1=1{search_clause}',
            search_params,
        ).fetchone()['c']
    else:
        rows = db.execute(
            f'SELECT * FROM institutions WHERE status = ?{search_clause} ORDER BY submitted_at DESC LIMIT ? OFFSET ?',
            (status_filter, *search_params, per_page, offset),
        ).fetchall()
        total = db.execute(
            f'SELECT COUNT(*) AS c FROM institutions WHERE status = ?{search_clause}',
            (status_filter, *search_params),
        ).fetchone()['c']

    counts = {
        'waiting': db.execute("SELECT COUNT(*) AS c FROM institutions WHERE status='waiting'").fetchone()['c'],
        'verified': db.execute("SELECT COUNT(*) AS c FROM institutions WHERE status='verified'").fetchone()['c'],
        'rejected': db.execute("SELECT COUNT(*) AS c FROM institutions WHERE status='rejected'").fetchone()['c'],
    }

    return render_template(
        'admin/dashboard.html',
        institutions=rows, total=total, counts=counts,
        status_filter=status_filter, page=page, per_page=per_page, q=q,
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
