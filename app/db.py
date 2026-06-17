# app\db.py

import sqlite3
from pathlib import Path

from .config import settings

_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        db_path = settings.db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _connection = sqlite3.connect(db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invite_code TEXT NOT NULL UNIQUE,
            guest_name TEXT NOT NULL,
            invitation_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invitation_id INTEGER NOT NULL UNIQUE,
            attendance BOOLEAN NOT NULL,
            guest_count INTEGER,
            children BOOLEAN NOT NULL,
            vegetarian BOOLEAN NOT NULL,
            allergies TEXT,
            phone TEXT,
            telegram TEXT,
            comment TEXT,
            answered_at TEXT NOT NULL,
            FOREIGN KEY(invitation_id) REFERENCES invitations(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            sort_order INTEGER NOT NULL,
            uploaded_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS program_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_time TEXT NOT NULL,
            title TEXT NOT NULL,
            sort_order INTEGER NOT NULL
        )
        """
    )
    conn.commit()
