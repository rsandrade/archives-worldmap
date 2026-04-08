import os

import click
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402

app = create_app()


@app.cli.command('hash-password')
@click.argument('password')
def hash_password(password):
    """Print a bcrypt hash for use as ADMIN_PASSWORD_HASH in .env.

    Usage:  flask hash-password mysecretpassword
    """
    from werkzeug.security import generate_password_hash
    print(generate_password_hash(password))


@app.cli.command('fix-escapes')
def fix_escapes():
    """Fix escaped apostrophes (d\\'Ivoire -> d'Ivoire) left over from PHP migration.

    Usage:  flask fix-escapes
    Or via Docker:  docker compose exec web flask fix-escapes
    """
    from app.db import get_db

    fields = ['name', 'address', 'city', 'district', 'identifier', 'url', 'admin_notes']
    backslash_apos = "\\'"   # the two-character sequence stored in old records
    with app.app_context():
        db = get_db()
        total = 0
        for field in fields:
            result = db.execute(
                f"UPDATE institutions SET {field} = REPLACE({field}, ?, ?) WHERE {field} LIKE ?",
                (backslash_apos, "'", "%\\%"),
            )
            if result.rowcount:
                print(f"  {field}: fixed {result.rowcount} row(s)")
                total += result.rowcount
        db.commit()
    print(f"Done. {total} field(s) updated.")


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true'))
