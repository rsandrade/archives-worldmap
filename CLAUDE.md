# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Archives World Map is a geospatial collaborative platform for cataloging public archive institutions worldwide. The project prioritizes simplicity: visitors submit institutions, the admin moderates via email links or an admin panel, and approved institutions appear on the map.

The legacy PHP versions are archived in the `archive/php` branch. All current work is on `master`.

**Maintainer:** Ricardo Sodré Andrade — https://feudo.org
**License:** GNU Affero General Public License v3.0 (AGPL-3.0)
**Repository:** https://github.com/rsandrade/archives-worldmap

## Setup & Running

```bash
# Option 1: Docker
docker compose up --build
# App runs at http://localhost:5000

# Option 2: Local
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Create .env (see Environment Variables below)
flask run
```

Generate the admin password hash:
```bash
# Using Docker (recommended):
docker compose exec web flask hash-password yourpassword
# Local:
flask hash-password yourpassword
# Copy the output to ADMIN_PASSWORD_HASH in .env
```

After pulling updates on the server:
```bash
git pull && docker compose restart
```

There are no automated tests.

## Architecture

Flask app with SQLite. Single table (`institutions`), no user accounts.

**Request flow:**
```
HTTP → run.py → Flask → Blueprint routes → Jinja2 templates
```

**Directory structure:**
```
.
├── run.py              # Entry point
├── config.py           # Config from environment
├── schema.sql          # SQLite schema (single table: institutions)
├── migrate.py          # Data migration script (MySQL dump → SQLite)
├── data/               # SQLite database (bind-mounted by Docker)
│   └── archivesmap.db
├── app/
│   ├── __init__.py     # App factory, DB init
│   ├── db.py           # get_db() / close_db()
│   ├── extensions.py   # Flask-Mail instance
│   ├── email_utils.py  # All email sending functions
│   ├── countries.py    # Country code → name/flag mapping
│   ├── routes/
│   │   ├── public.py      # Map, add, info, stats, search, about, contact, report
│   │   ├── moderation.py  # Token-based approve/reject (from email links)
│   │   └── admin.py       # Admin panel (login, dashboard, edit, delete)
│   ├── templates/
│   │   ├── base.html         # Layout (Bootstrap 3.3.7 + Leaflet.js)
│   │   ├── public/           # Public-facing pages
│   │   ├── admin/            # Admin login, dashboard, edit form
│   │   └── emails/           # HTML email templates
│   └── static/
│       ├── css/style.css
│       ├── js/i18n.js        # Client-side async i18n (JSON-based, no reload)
│       └── lang/             # Translation files (en, pt-br, es, zh, ro, pl)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

**Database:** Single `institutions` table with status workflow (`waiting` → `verified` | `rejected`). Each submission gets a unique `token` for email-based moderation.

**Blueprints:**
- `public` — all public routes (no auth required)
- `moderation` — `/approve/<token>` and `/reject/<token>` (stateless, from email)
- `admin` — `/admin/*` (session-based login, credentials from `.env`)

**Frontend:** Bootstrap 3.3.7 + Leaflet.js + Leaflet.markercluster. Map pins loaded via AJAX (`/api/pins`), rendered client-side with optional cluster toggle.

**Key design decisions:**
- No user registration or login — the old social features (forum, profiles, scores) were removed because nobody used them
- Admin is a single account configured via `.env` (username + password hash)
- Submissions are moderated via email links (approve/reject with one click) or through the admin panel
- reCAPTCHA v3 on public forms (add institution, contact, report) — score-based, invisible
- Client-side i18n using `data-i18n` (text) and `data-i18n-html` (HTML with links) attributes; async JSON fetch; 6 languages; no page reload
- Language detection priority: `?lang=xx` URL param > localStorage > browser language > English
- Flash messages use i18n keys (e.g. `flash_contact_success`) — JS translates them via `data-i18n` on the `<span>` in `base.html`
- Geocoding via Nominatim (OpenStreetMap) on the add form — no API key needed
- Report button on institution info page for flagging incorrect/non-existent entries
- Docker uses bind mount (`./data:/data`) for the SQLite database
- SMTP: port 587 + STARTTLS (port 465 is blocked on the server); sender must match authenticated SMTP user (Migadu enforces this)

**Anti-scraping measures:**
- Rate limiting via `flask-limiter` (home/pins 10/min, info 60/min, search 30/min, global 200/hour)
- Map pins served via `/api/pins` AJAX endpoint (not inline JSON) with 5-min cache header
- `robots.txt` disallows `/q`, `/bycountry`, `/admin`, `/api/`
- Pagination capped at 50 results per page (`qty` parameter clamped)
- Database queries use explicit column lists (no `SELECT *`) to avoid leaking internal fields (token, admin_notes, collaborator_email)

**Data migration:**
- `migrate.py` converts the old MySQL dump (`OldDump.sql`) to the new SQLite schema
- Run: `python migrate.py ../OldDump.sql ./data/archivesmap.db`
- Handles type casting (VARCHAR lat/lng → REAL), UUID token generation, NULL cleanup
- 777 institutions migrated from the legacy platform

## i18n

Translations live in `app/static/lang/{lang}.json`. To update text across all 6 languages at once, use a Python snippet:

```python
import json
base = "app/static/lang"
updates = {"key": "value"}  # repeat per language as needed
for lang in ["en", "pt-br", "es", "zh", "ro", "pl"]:
    path = f"{base}/{lang}.json"
    with open(path) as f: data = json.load(f)
    data.update(updates)
    with open(path, "w") as f: json.dump(data, f, ensure_ascii=False, indent=2)
```

Keys used with HTML content (links, etc.) must use `data-i18n-html` in the template, not `data-i18n`.

Flash message keys: `flash_recaptcha_fail`, `flash_add_success`, `flash_not_found`, `flash_report_success`, `flash_contact_success`.

## Environment Variables

Configured via `.env` file in the repo root:

```
SECRET_KEY=your-secret-key
DATABASE_PATH=/data/archivesmap.db

# SMTP — port 587 + STARTTLS; MAIL_DEFAULT_SENDER must match MAIL_USERNAME (Migadu requirement)
MAIL_SERVER=smtp.migadu.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=contact@archivesmap.org
MAIL_PASSWORD=password
MAIL_DEFAULT_SENDER=Archives World Map <contact@archivesmap.org>
MAIL_TIMEOUT=15

# Admin (single account)
ADMIN_EMAIL=admin@archivesmap.org
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=pbkdf2:sha256:...   # Generated with: flask hash-password

# reCAPTCHA v3
RECAPTCHA_SITE_KEY=...
RECAPTCHA_SECRET_KEY=...
RECAPTCHA_THRESHOLD=0.5

# Public URL (used in email links)
BASE_URL=https://www.archivesmap.org
```
