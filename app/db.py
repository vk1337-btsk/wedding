# app\db.py

import sqlite3

from .config import settings

_connection: sqlite3.Connection | None = None

_RESPONSE_COLUMNS = {
    "id",
    "invitation_id",
    "will_come",
    "comment_will_come",
    "allergies",
    "allergies_details",
    "alcohol",
    "additional_info",
    "answered_at",
}


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        db_path = settings.db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _connection = sqlite3.connect(db_path, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
    return _connection


def _table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def _table_columns(cursor: sqlite3.Cursor, table_name: str) -> set[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row["name"] for row in cursor.fetchall()}


def _create_responses_table(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invitation_id INTEGER NOT NULL,
            will_come TEXT,
            comment_will_come TEXT,
            allergies INTEGER,
            allergies_details TEXT,
            alcohol INTEGER,
            additional_info TEXT,
            answered_at TEXT NOT NULL,
            FOREIGN KEY(invitation_id) REFERENCES invitations(id)
        )
        """
    )


def _init_responses_table(cursor: sqlite3.Cursor) -> None:
    if not _table_exists(cursor, "responses"):
        _create_responses_table(cursor)
        return

    existing_columns = _table_columns(cursor, "responses")
    if _RESPONSE_COLUMNS.issubset(existing_columns):
        return

    cursor.execute("DROP TABLE IF EXISTS responses_old")
    cursor.execute("ALTER TABLE responses RENAME TO responses_old")
    _create_responses_table(cursor)

    old_columns = _table_columns(cursor, "responses_old")
    if "invitation_id" in old_columns:
        id_expr = "id" if "id" in old_columns else "NULL"
        attendance_expr = (
            "CASE WHEN attendance = 1 THEN 'yes' WHEN attendance = 0 THEN 'no' ELSE NULL END"
            if "attendance" in old_columns
            else "NULL"
        )
        answered_at_expr = (
            "COALESCE(answered_at, datetime('now'))"
            if "answered_at" in old_columns
            else "datetime('now')"
        )
        cursor.execute(
            f"""
            INSERT INTO responses (
                id,
                invitation_id,
                will_come,
                comment_will_come,
                allergies,
                allergies_details,
                alcohol,
                additional_info,
                answered_at
            )
            SELECT
                {id_expr},
                invitation_id,
                {attendance_expr},
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                {answered_at_expr}
            FROM responses_old
            """
        )
    cursor.execute("DROP TABLE responses_old")


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
    _init_responses_table(cursor)
    conn.commit()
