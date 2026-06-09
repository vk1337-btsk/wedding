import sqlite3
from datetime import datetime
from pathlib import Path
from secrets import token_urlsafe

from .db import get_connection


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def generate_code(length: int = 8) -> str:
    return token_urlsafe(length).replace("-", "_")[:length]


def create_invitation(guest_name: str, invitation_text: str, invite_code: str | None = None) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    if invite_code is None:
        invite_code = generate_code(8)
    created_at = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO invitations (invite_code, guest_name, invitation_text, created_at) VALUES (?, ?, ?, ?)",
        (invite_code, guest_name, invitation_text, created_at),
    )
    conn.commit()
    invitation_id = cursor.lastrowid
    return get_invitation(invitation_id)


def get_invitation(invitation_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invitations WHERE id = ?", (invitation_id,))
    return _row_to_dict(cursor.fetchone())


def get_invitation_by_code(invite_code: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invitations WHERE invite_code = ?", (invite_code,))
    return _row_to_dict(cursor.fetchone())


def list_invitations() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invitations ORDER BY created_at DESC")
    return [dict(row) for row in cursor.fetchall()]


def update_invitation(invitation_id: int, guest_name: str, invitation_text: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE invitations SET guest_name = ?, invitation_text = ? WHERE id = ?",
        (guest_name, invitation_text, invitation_id),
    )
    conn.commit()
    return get_invitation(invitation_id)


def delete_invitation(invitation_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM responses WHERE invitation_id = ?", (invitation_id,))
    cursor.execute("DELETE FROM invitations WHERE id = ?", (invitation_id,))
    conn.commit()


def get_response_for_invitation(invitation_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responses WHERE invitation_id = ?", (invitation_id,))
    return _row_to_dict(cursor.fetchone())


def create_response(
    invitation_id: int,
    attendance: bool,
    guest_count: int | None,
    children: bool,
    vegetarian: bool,
    allergies: str | None,
    phone: str | None,
    telegram: str | None,
    comment: str | None,
) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    answered_at = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO responses (invitation_id, attendance, guest_count, children, vegetarian, allergies, phone, telegram, comment, answered_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            invitation_id,
            int(attendance),
            guest_count,
            int(children),
            int(vegetarian),
            allergies or "",
            phone or "",
            telegram or "",
            comment or "",
            answered_at,
        ),
    )
    conn.commit()
    return get_response_for_invitation(invitation_id)


def list_responses() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT r.*, i.guest_name FROM responses r JOIN invitations i ON r.invitation_id = i.id ORDER BY r.answered_at DESC"
    )
    return [dict(row) for row in cursor.fetchall()]


def count_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM invitations")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM responses WHERE attendance = 1")
    confirmed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM responses WHERE attendance = 0")
    declined = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM invitations WHERE id NOT IN (SELECT invitation_id FROM responses)")
    unanswered = cursor.fetchone()[0]
    return {
        "total_invitations": total,
        "confirmed": confirmed,
        "declined": declined,
        "unanswered": unanswered,
    }


def list_photos() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM photos ORDER BY sort_order ASC, uploaded_at DESC")
    return [dict(row) for row in cursor.fetchall()]


def add_photo(filename: str, original_filename: str, sort_order: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    uploaded_at = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO photos (filename, original_filename, sort_order, uploaded_at) VALUES (?, ?, ?, ?)",
        (filename, original_filename, sort_order, uploaded_at),
    )
    conn.commit()
    photo_id = cursor.lastrowid
    cursor.execute("SELECT * FROM photos WHERE id = ?", (photo_id,))
    return _row_to_dict(cursor.fetchone())


def delete_photo(photo_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
    conn.commit()


def update_photo_order(photo_id: int, sort_order: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE photos SET sort_order = ? WHERE id = ?", (sort_order, photo_id))
    conn.commit()
    cursor.execute("SELECT * FROM photos WHERE id = ?", (photo_id,))
    return _row_to_dict(cursor.fetchone())


def list_program_items() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM program_items ORDER BY sort_order ASC")
    return [dict(row) for row in cursor.fetchall()]


def add_program_item(event_time: str, title: str, sort_order: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO program_items (event_time, title, sort_order) VALUES (?, ?, ?)",
        (event_time, title, sort_order),
    )
    conn.commit()
    return _row_to_dict(cursor.execute("SELECT * FROM program_items WHERE id = ?", (cursor.lastrowid,)).fetchone())


def update_program_item(item_id: int, event_time: str, title: str, sort_order: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE program_items SET event_time = ?, title = ?, sort_order = ? WHERE id = ?",
        (event_time, title, sort_order, item_id),
    )
    conn.commit()
    cursor.execute("SELECT * FROM program_items WHERE id = ?", (item_id,))
    return _row_to_dict(cursor.fetchone())


def delete_program_item(item_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM program_items WHERE id = ?", (item_id,))
    conn.commit()
