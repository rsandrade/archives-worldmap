# Archives World Map

A collaborative geospatial platform for cataloging public archive institutions worldwide.

**Live site:** https://www.archivesmap.org  
**Maintainer:** [Ricardo Sodré Andrade](https://feudo.org)  
**License:** [AGPL-3.0](LICENSE)

## Features

- Interactive world map with archive institution pins
- Community submissions reviewed by the administrator
- Moderation via email links (one-click approve/reject) or admin panel
- 6 languages: English, Portuguese, Spanish, Chinese, Romanian, Polish
- Address geocoding on the submission form (OpenStreetMap/Nominatim)
- Report button to flag incorrect or non-existent entries

## Stack

Python · Flask · SQLite · Leaflet.js · Bootstrap 3 · Docker

## Running

```bash
cp .env.example .env
# Edit .env with your credentials

docker compose up --build
# App available at http://localhost:5000
```

Generate the admin password hash:
```bash
flask hash-password yourpassword
```

## Data migration

To migrate from the legacy MySQL dump:
```bash
python migrate.py path/to/OldDump.sql ./data/archivesmap.db
```

---

> The previous PHP version of this project is preserved in the [`archive/php`](../../tree/archive/php) branch.

---

🤖 Criado com auxílio do Claude Code
