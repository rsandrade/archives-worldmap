import json
import uuid

import requests
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    current_app, flash,
)

from ..db import get_db
from ..email_utils import send_new_submission_email
from ..countries import country_display
from .. import limiter

public_bp = Blueprint('public', __name__)


def _parse_pagination():
    """Parse and clamp pagination parameters."""
    try:
        page = max(int(request.args.get('since', 0)), 0)
        per_page = min(max(int(request.args.get('qty', 10)), 1), 50)
    except (ValueError, TypeError):
        page, per_page = 0, 10
    return page, per_page


def _verify_recaptcha(response_token, action=None):
    if not current_app.config['RECAPTCHA_ENABLED']:
        return True
    if not response_token:
        return False
    secret = current_app.config['RECAPTCHA_SECRET_KEY']
    r = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={'secret': secret, 'response': response_token},
    )
    result = r.json()
    if not result.get('success', False):
        return False
    score = result.get('score', 0)
    threshold = current_app.config.get('RECAPTCHA_THRESHOLD', 0.5)
    return score >= threshold


def _build_pins(rows):
    pins = []
    for row in rows:
        pins.append({
            'id': row['id'],
            'lat': row['latitude'],
            'lng': row['longitude'],
            'name': row['name'],
        })
    return json.dumps(pins)


@public_bp.route('/')
@limiter.limit("10 per minute")
def home():
    return render_template('public/home.html')


@public_bp.route('/api/pins')
@limiter.limit("10 per minute")
def api_pins():
    db = get_db()
    rows = db.execute(
        'SELECT id, latitude, longitude, name FROM institutions WHERE status = ?',
        ('verified',),
    ).fetchall()
    resp = current_app.response_class(_build_pins(rows), mimetype='application/json')
    resp.headers['Cache-Control'] = 'public, max-age=300'
    return resp


@public_bp.route('/robots.txt')
def robots():
    return current_app.response_class(
        "User-agent: *\nAllow: /\nAllow: /info/\nDisallow: /q\nDisallow: /bycountry\nDisallow: /admin\nDisallow: /api/\n",
        mimetype='text/plain',
    )


@public_bp.route('/add', methods=['GET'])
def add():
    return render_template('public/add.html')


@public_bp.route('/add', methods=['POST'])
def add_submit():
    if not _verify_recaptcha(request.form.get('g-recaptcha-response', '')):
        flash('reCAPTCHA verification failed.', 'danger')
        return redirect(url_for('public.add'))

    db = get_db()
    token = uuid.uuid4().hex

    db.execute(
        '''INSERT INTO institutions
           (name, latitude, longitude, identifier, address, city, district,
            country, url, email, collaborator_name, collaborator_email, token)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            request.form['name'],
            request.form['latitude'],
            request.form['longitude'],
            request.form.get('identifier', ''),
            request.form.get('address', ''),
            request.form.get('city', ''),
            request.form.get('district', ''),
            request.form.get('country', ''),
            request.form.get('url', ''),
            request.form.get('email', ''),
            request.form['contributor'],
            request.form['contributoremail'],
            token,
        ),
    )
    db.commit()

    institution = db.execute(
        'SELECT * FROM institutions WHERE token = ?', (token,)
    ).fetchone()

    send_new_submission_email(dict(institution))

    flash('Thank you! Your submission is under review.', 'success')
    return redirect(url_for('public.add_done'))


@public_bp.route('/add-done')
def add_done():
    return render_template('public/add_done.html')


@public_bp.route('/info/<int:inst_id>')
@limiter.limit("60 per minute")
def info(inst_id):
    db = get_db()
    inst = db.execute(
        '''SELECT id, name, latitude, longitude, address, city, district,
                  country, url, email, identifier, collaborator_name
           FROM institutions WHERE id = ? AND status = ?''',
        (inst_id, 'verified'),
    ).fetchone()
    if not inst:
        flash('Institution not found.', 'warning')
        return redirect(url_for('public.home'))
    return render_template('public/info.html', institution=inst)


@public_bp.route('/stats')
def stats():
    db = get_db()
    qty = db.execute(
        "SELECT COUNT(*) AS c FROM institutions WHERE status = 'verified'"
    ).fetchone()['c']

    ranking = db.execute(
        '''SELECT country, COUNT(country) AS total FROM institutions
           WHERE status = 'verified'
           GROUP BY country ORDER BY total DESC LIMIT 10'''
    ).fetchall()

    return render_template('public/stats.html', qty_institutions=qty,
                           ranking_countries=ranking, country_display=country_display)


@public_bp.route('/q')
@limiter.limit("30 per minute")
def search():
    query = request.args.get('search', '')
    page, per_page = _parse_pagination()

    db = get_db()
    rows = db.execute(
        '''SELECT id, name, country FROM institutions
           WHERE name LIKE ? AND status = 'verified'
           LIMIT ? OFFSET ?''',
        (f'%{query}%', per_page, page),
    ).fetchall()

    total = db.execute(
        "SELECT COUNT(*) AS c FROM institutions WHERE name LIKE ? AND status = 'verified'",
        (f'%{query}%',),
    ).fetchone()['c']

    return render_template(
        'public/search.html', institutions=rows, total=total,
        search=query, per_page=per_page, offset=page,
    )


@public_bp.route('/bycountry')
@limiter.limit("30 per minute")
def by_country():
    country = request.args.get('country', '')
    page, per_page = _parse_pagination()

    db = get_db()
    rows = db.execute(
        "SELECT id, name, country FROM institutions WHERE country = ? AND status = 'verified' LIMIT ? OFFSET ?",
        (country, per_page, page),
    ).fetchall()

    total = db.execute(
        "SELECT COUNT(*) AS c FROM institutions WHERE country = ? AND status = 'verified'",
        (country,),
    ).fetchone()['c']

    return render_template(
        'public/search.html', institutions=rows, total=total,
        search=country, per_page=per_page, offset=page,
    )


@public_bp.route('/report/<int:inst_id>', methods=['POST'])
def report(inst_id):
    if not _verify_recaptcha(request.form.get('g-recaptcha-response', '')):
        flash('reCAPTCHA verification failed.', 'danger')
        return redirect(url_for('public.info', inst_id=inst_id))

    db = get_db()
    inst = db.execute(
        'SELECT id, name, latitude, longitude, city, country FROM institutions WHERE id = ?',
        (inst_id,),
    ).fetchone()
    if not inst:
        flash('Institution not found.', 'warning')
        return redirect(url_for('public.home'))

    from ..email_utils import send_report_email
    send_report_email(
        institution=dict(inst),
        reporter_email=request.form.get('email', ''),
        reason=request.form.get('reason', ''),
    )
    flash('Thank you for your report. We will review it.', 'success')
    return redirect(url_for('public.info', inst_id=inst_id))


@public_bp.route('/about')
def about():
    return render_template('public/about.html')


@public_bp.route('/contact', methods=['GET'])
def contact():
    return render_template('public/contact.html')


@public_bp.route('/contact', methods=['POST'])
def contact_submit():
    if not _verify_recaptcha(request.form.get('g-recaptcha-response', '')):
        flash('reCAPTCHA verification failed.', 'danger')
        return redirect(url_for('public.contact'))

    from ..email_utils import send_contact_email
    send_contact_email(
        name=request.form.get('name', ''),
        email=request.form.get('email', ''),
        institution=request.form.get('institution', ''),
        subject=request.form.get('subject', ''),
        body=request.form.get('body', ''),
    )
    flash('Thank you for your message!', 'success')
    return redirect(url_for('public.contact'))
