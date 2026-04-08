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


@app.cli.command('fix-names')
def fix_names():
    """Restore apostrophes removed from institution names during legacy PHP edits.

    Usage:  flask fix-names
    Or via Docker:  docker compose exec web flask fix-names
    """
    from app.db import get_db

    corrections = [
        (487, "Archives de l'Université catholique de Louvain"),
        (342, "Archives de l'Etat du Valais"),
        (517, "Arxiu Comarcal de l'Alt Penedès"),
        (543, "Arxiu Comarcal de l'Alt Urgell"),
        (545, "Arxiu Comarcal de la Ribera d'Ebre"),
        (626, "Arxiu Municipal del Districte de l'Eixample"),
        (511, "Dipòsit d'Arxius de Cervera"),
        (623, "Direcció del Sistema Municipal d'Arxius"),
        (476, "Servei d'Arxiu Municipal de Lloret de Mar"),
        (192, "Biblioteca Comunale dell'Archiginnasio"),
        (598, "Isacem - Istituto per la storia dell'Azione cattolica e del movimento cattolico in Italia Paolo VI"),
    ]

    with app.app_context():
        db = get_db()
        for inst_id, name in corrections:
            old = db.execute("SELECT name FROM institutions WHERE id = ?", (inst_id,)).fetchone()
            if old is None:
                print(f"  {inst_id}: not found, skipped")
                continue
            if old['name'] == name:
                print(f"  {inst_id}: already correct, skipped")
                continue
            db.execute("UPDATE institutions SET name = ? WHERE id = ?", (name, inst_id))
            print(f"  {inst_id}: '{old['name']}' -> '{name}'")
        db.commit()
    print("Done.")


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true'))
