import sqlite3
from flask import g, current_app
from pathlib import Path


def _db_path():
    # instance/rsvp.sqlite
    return Path(current_app.instance_path) / "rsvp.sqlite"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(_db_path())
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    def _create_tables():
        db = sqlite3.connect(Path(app.instance_path) / "rsvp.sqlite")
        db.execute("""
        CREATE TABLE IF NOT EXISTS invites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            label TEXT,
            max_guests INTEGER NOT NULL DEFAULT 1,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS rsvps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invite_code TEXT,
            name TEXT NOT NULL,
            attending INTEGER NOT NULL,
            guests_count INTEGER NOT NULL,
            allergies TEXT,
            note TEXT,
            created_at TEXT NOT NULL
        );
        """)
        db.commit()
        db.close()

    app.teardown_appcontext(close_db)
    with app.app_context():
        _create_tables()
