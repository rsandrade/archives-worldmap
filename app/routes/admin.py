import functools
import secrets
import string

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, current_app, flash, abort,
)
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db
from ..email_utils import send_approved_email, send_rejected_email
from .. import limiter

admin_bp = Blueprint('admin', __name__)


def _is_logged_in():
    return session.get('admin_logged') or session.get('user_id')


def admin_required(f):
    """Restrict to super admin only."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged'):
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return wrapped


def login_required(f):
    """Allow any authenticated user (admin or staff)."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not _is_logged_in():
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return wrapped


def permission_required(perm):
    """Allow admin or staff with the given permission flag."""
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if not session.get('admin_logged') and not session.get(perm):
                flash('Permission denied.', 'danger')
                return redirect(url_for('admin.dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@admin_bp.route('/login', methods=['GET'])
def login():
    return redirect(url_for('admin.dashboard'))


def _get_active_hash(db):
    """Return current admin password hash: DB settings override takes precedence over .env."""
    row = db.execute("SELECT value FROM settings WHERE key = 'admin_password_hash'").fetchone()
    if row:
        return row['value']
    return current_app.config['ADMIN_PASSWORD_HASH']


@admin_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login_submit():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    db = get_db()

    # Try super admin (permanent password or temp reset)
    expected_user = current_app.config['ADMIN_USERNAME']
    active_hash = _get_active_hash(db)
    if username == expected_user and active_hash and check_password_hash(active_hash, password):
        session.clear()
        session['admin_logged'] = True
        session['user_username'] = username
        session.permanent = True
        return redirect(url_for('admin.dashboard'))

    if username == expected_user:
        reset = db.execute(
            "SELECT id, hash FROM password_resets WHERE expires_at > datetime('now') ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if reset and check_password_hash(reset['hash'], password):
            db.execute('DELETE FROM password_resets WHERE id = ?', (reset['id'],))
            db.commit()
            session.clear()
            session['admin_logged'] = True
            session['user_username'] = username
            session['must_change_password'] = True
            session.permanent = True
            flash('Logged in with temporary password. Please set a permanent password.', 'warning')
            return redirect(url_for('admin.change_password'))

    # Try staff users
    user = db.execute(
        'SELECT * FROM users WHERE username = ? AND is_active = 1', (username,)
    ).fetchone()
    if user and check_password_hash(user['password_hash'], password):
        session.clear()
        session['user_id'] = user['id']
        session['user_username'] = user['username']
        session['can_approve'] = bool(user['can_approve'])
        session['can_edit_waiting'] = bool(user['can_edit_waiting'])
        session['can_edit_verified'] = bool(user['can_edit_verified'])
        session['must_change_password'] = bool(user['must_change_password'])
        session.permanent = True
        if user['must_change_password']:
            flash('Please set a new password before continuing.', 'warning')
            return redirect(url_for('admin.change_password'))
        return redirect(url_for('admin.dashboard'))

    flash('Invalid credentials.', 'danger')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('admin/forgot_password.html')


@admin_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password_submit():
    identifier = request.form.get('identifier', '').strip()
    if not identifier:
        flash('Please enter your username or email.', 'danger')
        return redirect(url_for('admin.forgot_password'))

    db = get_db()
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    new_password = ''.join(secrets.choice(alphabet) for _ in range(20))
    hashed = generate_password_hash(new_password)

    admin_username = current_app.config['ADMIN_USERNAME']
    admin_email = current_app.config.get('ADMIN_EMAIL', '')

    if identifier in (admin_username, admin_email):
        if not admin_email:
            flash('ADMIN_EMAIL is not configured.', 'danger')
            return redirect(url_for('admin.forgot_password'))
        db.execute('DELETE FROM password_resets')
        db.execute(
            "INSERT INTO password_resets (hash, expires_at) VALUES (?, datetime('now', '+1 hour'))",
            (hashed,),
        )
        db.commit()
        from ..email_utils import send_password_reset_email
        send_password_reset_email(new_password)
        flash('A temporary password has been sent to the admin email.', 'success')
        return redirect(url_for('admin.dashboard'))

    # Check staff users by username or email
    user = db.execute(
        'SELECT * FROM users WHERE (username = ? OR email = ?) AND is_active = 1',
        (identifier, identifier),
    ).fetchone()
    if user:
        db.execute(
            'UPDATE users SET password_hash = ?, must_change_password = 1 WHERE id = ?',
            (hashed, user['id']),
        )
        db.commit()
        from ..email_utils import send_staff_account_email
        send_staff_account_email(user['username'], user['email'], new_password, is_new=False)

    # Generic message to prevent username/email enumeration
    flash('If that account exists, a temporary password has been sent by email.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/change-password', methods=['GET'])
@login_required
def change_password():
    return render_template('admin/change_password.html')


@admin_bp.route('/change-password', methods=['POST'])
@login_required
def change_password_submit():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm = request.form.get('confirm_password', '')
    from_reset = session.get('must_change_password', False)

    if not from_reset:
        db = get_db()
        if session.get('admin_logged'):
            active_hash = _get_active_hash(db)
            if not active_hash or not check_password_hash(active_hash, current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('admin.change_password'))
        else:
            user = db.execute(
                'SELECT password_hash FROM users WHERE id = ?', (session['user_id'],)
            ).fetchone()
            if not user or not check_password_hash(user['password_hash'], current_password):
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

    if session.get('admin_logged'):
        db.execute(
            "INSERT INTO settings (key, value) VALUES ('admin_password_hash', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (new_hash,),
        )
    else:
        db.execute(
            'UPDATE users SET password_hash = ?, must_change_password = 0 WHERE id = ?',
            (new_hash, session['user_id']),
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
    if not _is_logged_in():
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
@permission_required('can_approve')
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

    flash('Institution approved.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/reject/<int:inst_id>')
@permission_required('can_approve')
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

    flash('Institution rejected.', 'info')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/edit/<int:inst_id>', methods=['GET'])
@login_required
def edit(inst_id):
    db = get_db()
    inst = db.execute('SELECT * FROM institutions WHERE id=?', (inst_id,)).fetchone()
    if not inst:
        flash('Institution not found.', 'warning')
        return redirect(url_for('admin.dashboard'))
    if not session.get('admin_logged'):
        if inst['status'] == 'waiting' and not session.get('can_edit_waiting'):
            flash('Permission denied.', 'danger')
            return redirect(url_for('admin.dashboard'))
        if inst['status'] == 'verified' and not session.get('can_edit_verified'):
            flash('Permission denied.', 'danger')
            return redirect(url_for('admin.dashboard'))
        if inst['status'] == 'rejected':
            flash('Permission denied.', 'danger')
            return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit.html', institution=inst)


@admin_bp.route('/edit/<int:inst_id>', methods=['POST'])
@login_required
def edit_submit(inst_id):
    db = get_db()
    inst = db.execute('SELECT status FROM institutions WHERE id=?', (inst_id,)).fetchone()
    if not inst:
        flash('Institution not found.', 'warning')
        return redirect(url_for('admin.dashboard'))
    if not session.get('admin_logged'):
        if inst['status'] == 'waiting' and not session.get('can_edit_waiting'):
            abort(403)
        if inst['status'] == 'verified' and not session.get('can_edit_verified'):
            abort(403)
        if inst['status'] == 'rejected':
            abort(403)
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


# ── User management (admin only) ─────────────────────────────────────────────

@admin_bp.route('/users', methods=['GET'])
@admin_required
def users():
    db = get_db()
    all_users = db.execute(
        'SELECT id, username, email, can_approve, can_edit_waiting, can_edit_verified, is_active, created_at '
        'FROM users ORDER BY created_at DESC'
    ).fetchall()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/create', methods=['POST'])
@admin_required
def user_create():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    can_approve = 1 if request.form.get('can_approve') else 0
    can_edit_waiting = 1 if request.form.get('can_edit_waiting') else 0
    can_edit_verified = 1 if request.form.get('can_edit_verified') else 0

    if not username or not email:
        flash('Username and email are required.', 'danger')
        return redirect(url_for('admin.users'))

    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    temp_password = ''.join(secrets.choice(alphabet) for _ in range(20))
    hashed = generate_password_hash(temp_password)

    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (username, email, password_hash, can_approve, can_edit_waiting, '
            'can_edit_verified, must_change_password) VALUES (?, ?, ?, ?, ?, ?, 1)',
            (username, email, hashed, can_approve, can_edit_waiting, can_edit_verified),
        )
        db.commit()
    except Exception:
        flash('Username or email already exists.', 'danger')
        return redirect(url_for('admin.users'))

    from ..email_utils import send_staff_account_email
    send_staff_account_email(username, email, temp_password, is_new=True)

    flash(f'User "{username}" created. Temporary password sent by email.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def user_edit(user_id):
    db = get_db()
    user = db.execute(
        'SELECT id, username, email, can_approve, can_edit_waiting, can_edit_verified, is_active '
        'FROM users WHERE id = ?',
        (user_id,),
    ).fetchone()
    if not user:
        flash('User not found.', 'warning')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_edit.html', user=user)


@admin_bp.route('/users/<int:user_id>', methods=['POST'])
@admin_required
def user_edit_submit(user_id):
    email = request.form.get('email', '').strip()
    can_approve = 1 if request.form.get('can_approve') else 0
    can_edit_waiting = 1 if request.form.get('can_edit_waiting') else 0
    can_edit_verified = 1 if request.form.get('can_edit_verified') else 0
    is_active = 1 if request.form.get('is_active') else 0

    if not email:
        flash('Email is required.', 'danger')
        return redirect(url_for('admin.user_edit', user_id=user_id))

    db = get_db()
    try:
        db.execute(
            'UPDATE users SET email=?, can_approve=?, can_edit_waiting=?, can_edit_verified=?, '
            'is_active=? WHERE id=?',
            (email, can_approve, can_edit_waiting, can_edit_verified, is_active, user_id),
        )
        db.commit()
    except Exception:
        flash('Email already in use.', 'danger')
        return redirect(url_for('admin.user_edit', user_id=user_id))

    flash('User updated.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def user_reset_password(user_id):
    db = get_db()
    user = db.execute('SELECT username, email FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        flash('User not found.', 'warning')
        return redirect(url_for('admin.users'))

    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    temp_password = ''.join(secrets.choice(alphabet) for _ in range(20))
    hashed = generate_password_hash(temp_password)

    db.execute(
        'UPDATE users SET password_hash = ?, must_change_password = 1 WHERE id = ?',
        (hashed, user_id),
    )
    db.commit()

    from ..email_utils import send_staff_account_email
    send_staff_account_email(user['username'], user['email'], temp_password, is_new=False)

    flash(f'Password reset for "{user["username"]}". Temporary password sent by email.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def user_delete(user_id):
    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('admin.users'))
