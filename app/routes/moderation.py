from flask import Blueprint, redirect, url_for, flash, render_template, request

from ..db import get_db
from ..email_utils import send_approved_email, send_rejected_email

moderation_bp = Blueprint('moderation', __name__)


@moderation_bp.route('/approve/<token>', methods=['GET'])
def approve_confirm(token):
    db = get_db()
    inst = db.execute('SELECT * FROM institutions WHERE token = ?', (token,)).fetchone()
    if not inst:
        flash('Invalid or expired link.', 'danger')
        return redirect(url_for('public.home'))
    if inst['status'] != 'waiting':
        flash('This submission has already been moderated.', 'info')
        return redirect(url_for('public.home'))
    return render_template('moderation/confirm.html', institution=inst, action='approve', token=token)


@moderation_bp.route('/approve/<token>', methods=['POST'])
def approve(token):
    db = get_db()
    inst = db.execute('SELECT * FROM institutions WHERE token = ?', (token,)).fetchone()
    if not inst or inst['status'] != 'waiting':
        flash('Invalid or already moderated.', 'warning')
        return redirect(url_for('public.home'))
    db.execute(
        "UPDATE institutions SET status = 'verified', moderated_at = datetime('now') WHERE token = ?",
        (token,),
    )
    db.commit()
    send_approved_email(dict(inst))
    flash(f'Institution "{inst["name"]}" approved!', 'success')
    return redirect(url_for('public.home'))


@moderation_bp.route('/reject/<token>', methods=['GET'])
def reject_confirm(token):
    db = get_db()
    inst = db.execute('SELECT * FROM institutions WHERE token = ?', (token,)).fetchone()
    if not inst:
        flash('Invalid or expired link.', 'danger')
        return redirect(url_for('public.home'))
    if inst['status'] != 'waiting':
        flash('This submission has already been moderated.', 'info')
        return redirect(url_for('public.home'))
    return render_template('moderation/confirm.html', institution=inst, action='reject', token=token)


@moderation_bp.route('/reject/<token>', methods=['POST'])
def reject(token):
    db = get_db()
    inst = db.execute('SELECT * FROM institutions WHERE token = ?', (token,)).fetchone()
    if not inst or inst['status'] != 'waiting':
        flash('Invalid or already moderated.', 'warning')
        return redirect(url_for('public.home'))
    db.execute(
        "UPDATE institutions SET status = 'rejected', moderated_at = datetime('now') WHERE token = ?",
        (token,),
    )
    db.commit()
    send_rejected_email(dict(inst))
    flash(f'Institution "{inst["name"]}" rejected.', 'info')
    return redirect(url_for('public.home'))
