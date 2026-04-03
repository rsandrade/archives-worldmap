#!/usr/bin/env python3
"""
Migrate data from OldDump.sql (MySQL) to SQLite for Archives World Map.

Usage:
    python migrate.py ../OldDump.sql [output.db]

Reads the MySQL dump, extracts Institutions records, and inserts them
into a new SQLite database using the schema from schema.sql.
"""

import re
import sqlite3
import sys
import uuid
from pathlib import Path


# MySQL column order in the INSERT statement
# id, latitude, longitude, name, address, city, district, country,
# url, email, status, collaborator_name, collaborator_email,
# identifier, importedfrom, datetime
EXPECTED_FIELDS = 16


def parse_sql_string(text: str, pos: int):
    """Parse a single-quoted SQL string starting at pos (on the quote).
    Handles escaped quotes (\') and escaped backslashes (\\).
    Returns (parsed_string, new_pos) where new_pos is after the closing quote.
    """
    assert text[pos] == "'"
    pos += 1  # skip opening quote
    chars = []
    while pos < len(text):
        ch = text[pos]
        if ch == '\\':
            pos += 1
            if pos < len(text):
                chars.append(text[pos])
                pos += 1
            continue
        if ch == "'":
            pos += 1
            return ''.join(chars), pos
        chars.append(ch)
        pos += 1
    raise ValueError("Unterminated string")


def parse_value(text: str, pos: int):
    """Parse one SQL value (string, number, or NULL) starting at pos.
    Returns (value, new_pos).
    """
    # skip whitespace
    while pos < len(text) and text[pos] in ' \t\n\r':
        pos += 1

    if text[pos] == "'":
        return parse_sql_string(text, pos)
    # NULL
    if text[pos:pos+4].upper() == 'NULL':
        return None, pos + 4
    # number (possibly negative, possibly decimal)
    m = re.match(r'-?[\d.]+', text[pos:])
    if m:
        val = m.group(0)
        return val, pos + len(val)
    raise ValueError(f"Cannot parse value at pos {pos}: ...{text[pos:pos+20]}...")


def parse_tuple(text: str, pos: int):
    """Parse a parenthesized tuple of values starting at '('.
    Returns (list_of_values, new_pos).
    """
    assert text[pos] == '('
    pos += 1
    values = []
    while True:
        val, pos = parse_value(text, pos)
        values.append(val)
        # skip whitespace
        while pos < len(text) and text[pos] in ' \t\n\r':
            pos += 1
        if text[pos] == ')':
            return values, pos + 1
        if text[pos] == ',':
            pos += 1
            continue
        raise ValueError(f"Unexpected char at pos {pos}: {text[pos]}")


def parse_insert_line(line: str):
    """Parse a MySQL INSERT INTO ... VALUES (...),(...),... line.
    Yields lists of values for each tuple.
    """
    # Find the start of VALUES
    m = re.search(r'VALUES\s*', line, re.IGNORECASE)
    if not m:
        return
    pos = m.end()
    while pos < len(line):
        # skip whitespace and commas between tuples
        while pos < len(line) and line[pos] in ' \t\n\r,':
            pos += 1
        if pos >= len(line) or line[pos] == ';':
            break
        if line[pos] == '(':
            values, pos = parse_tuple(line, pos)
            yield values
        else:
            break


def migrate(dump_path: str, db_path: str):
    schema_path = Path(__file__).parent / 'schema.sql'
    if not schema_path.exists():
        print(f"ERROR: schema.sql not found at {schema_path}")
        sys.exit(1)

    dump = Path(dump_path)
    if not dump.exists():
        print(f"ERROR: Dump file not found: {dump_path}")
        sys.exit(1)

    # Find the INSERT line for Institutions
    insert_line = None
    with open(dump, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('INSERT INTO `Institutions`'):
                insert_line = line
                break

    if not insert_line:
        print("ERROR: No INSERT INTO `Institutions` found in dump.")
        sys.exit(1)

    # Parse all tuples
    records = list(parse_insert_line(insert_line))
    print(f"Parsed {len(records)} records from dump.")

    # Create/overwrite the SQLite database
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    if db_file.exists():
        db_file.unlink()
        print(f"Removed existing database: {db_path}")

    conn = sqlite3.connect(str(db_file))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(schema_path.read_text())

    inserted = 0
    errors = 0
    stats = {'verified': 0, 'waiting': 0, 'rejected': 0, 'other': 0}

    for row in records:
        if len(row) != EXPECTED_FIELDS:
            print(f"  SKIP: row has {len(row)} fields (expected {EXPECTED_FIELDS}): id={row[0] if row else '?'}")
            errors += 1
            continue

        (raw_id, raw_lat, raw_lng, name, address, city, district, country,
         url, email, status, collab_name, collab_email,
         identifier, _importedfrom, raw_datetime) = row

        # Cast types — fix locale-corrupted coords (e.g. '-8.4269352,87')
        try:
            inst_id = int(raw_id)
            lat_str = raw_lat.split(',')[0] if raw_lat else raw_lat
            lng_str = raw_lng.split(',')[0] if raw_lng else raw_lng
            latitude = float(lat_str)
            longitude = float(lng_str)
        except (ValueError, TypeError) as e:
            print(f"  SKIP id={raw_id}: bad lat/lng — {e}")
            errors += 1
            continue

        # Generate token
        token = uuid.uuid4().hex

        # NULL → empty string for NOT NULL fields
        collab_name = collab_name or ''
        collab_email = collab_email or ''
        name = name or ''

        # submitted_at
        submitted_at = raw_datetime or ''

        # moderated_at: set to submitted_at if verified/rejected
        moderated_at = submitted_at if status in ('verified', 'rejected') else None

        conn.execute(
            """INSERT INTO institutions
               (id, name, latitude, longitude, address, city, district, country,
                url, email, identifier, status, token,
                collaborator_name, collaborator_email, admin_notes,
                submitted_at, moderated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (inst_id, name, latitude, longitude, address, city, district, country,
             url, email, identifier, status, token,
             collab_name, collab_email, None,
             submitted_at, moderated_at)
        )
        inserted += 1
        stats[status] = stats.get(status, 0) + 1

    conn.commit()

    # Verify
    cur = conn.execute("SELECT COUNT(*) FROM institutions")
    total_in_db = cur.fetchone()[0]

    print(f"\n{'='*50}")
    print(f"Migration complete!")
    print(f"  Parsed:   {len(records)}")
    print(f"  Inserted: {inserted}")
    print(f"  Errors:   {errors}")
    print(f"  In DB:    {total_in_db}")
    print(f"\nBy status:")
    for s, c in sorted(stats.items()):
        if c > 0:
            print(f"  {s}: {c}")

    # Sanity checks
    print(f"\nSanity checks:")
    cur = conn.execute("SELECT COUNT(*) FROM institutions WHERE latitude IS NULL OR longitude IS NULL")
    print(f"  NULL lat/lng: {cur.fetchone()[0]}")
    cur = conn.execute("SELECT COUNT(*) FROM institutions WHERE token IS NULL OR token = ''")
    print(f"  Missing tokens: {cur.fetchone()[0]}")
    cur = conn.execute("SELECT COUNT(*) FROM institutions WHERE name = ''")
    print(f"  Empty names: {cur.fetchone()[0]}")

    # Show first record as sanity check
    cur = conn.execute("SELECT id, name, latitude, longitude, city, country, status FROM institutions WHERE id = 1")
    row = cur.fetchone()
    if row:
        print(f"\nRecord #1: {row[1]} ({row[4]}, {row[5]}) [{row[6]}]")
        print(f"  lat={row[2]}, lng={row[3]}")

    conn.close()
    print(f"\nDatabase saved to: {db_file.resolve()}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <dump.sql> [output.db]")
        sys.exit(1)

    dump_path = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else str(Path(__file__).parent / 'archivesmap.db')

    migrate(dump_path, db_path)
