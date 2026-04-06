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


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true'))
