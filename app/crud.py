# app\crud.py
import sqlite3
from datetime import datetime
from secrets import token_urlsafe

from .db import get_connection


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def generate_code(length: int = 8) -> str:
    return token_urlsafe(length).replace("-", "_")[:length]


def create_invitation(
    guest_name: str, invitation_text: str, invite_code: str | None = None
) -> dict:
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


def update_invitation(
    invitation_id: int, guest_name: str, invitation_text: str
) -> dict | None:
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


def get_response(response_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responses WHERE id = ?", (response_id,))
    return _row_to_dict(cursor.fetchone())


def get_responses_for_invitation(invitation_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM responses WHERE invitation_id = ? ORDER BY answered_at DESC",
        (invitation_id,),
    )
    return [dict(row) for row in cursor.fetchall()]


def create_response(
    invitation_id: int,
    will_come: str,
    comment_will_come: str | None,
    allergies: bool | None,
    allergies_details: str | None,
    alcohol: bool | None,
    additional_info: str | None,
) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    answered_at = datetime.utcnow().isoformat()
    cursor.execute(
        """
        INSERT INTO responses (
            invitation_id,
            will_come,
            comment_will_come,
            allergies,
            allergies_details,
            alcohol,
            additional_info,
            answered_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            invitation_id,
            will_come,
            comment_will_come or "",
            None if allergies is None else int(allergies),
            allergies_details or "",
            None if alcohol is None else int(alcohol),
            additional_info or "",
            answered_at,
        ),
    )
    conn.commit()
    return get_response(cursor.lastrowid)


def list_responses() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            r.id,
            r.invitation_id,
            i.guest_name,
            r.will_come,
            r.comment_will_come,
            r.allergies,
            r.allergies_details,
            r.alcohol,
            r.additional_info,
            r.answered_at
        FROM responses r
        JOIN invitations i ON r.invitation_id = i.id
        ORDER BY r.answered_at DESC
        """
    )
    return [dict(row) for row in cursor.fetchall()]


def count_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM invitations")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM responses WHERE will_come = 'yes'")
    confirmed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM responses WHERE will_come = 'no'")
    declined = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM invitations WHERE id NOT IN (SELECT invitation_id FROM responses)"
    )
    unanswered = cursor.fetchone()[0]
    return {
        "total_invitations": total,
        "confirmed": confirmed,
        "declined": declined,
        "unanswered": unanswered,
    }


def get_response(response_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responses WHERE id = ?", (response_id,))
    return _row_to_dict(cursor.fetchone())


def update_response(
    response_id: int,
    will_come: str,
    comment_will_come: str | None,
    allergies: bool | None,
    allergies_details: str | None,
    alcohol: bool | None,
    additional_info: str | None,
) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    answered_at = datetime.utcnow().isoformat()  # обновим время
    cursor.execute(
        """
        UPDATE responses
        SET will_come = ?,
            comment_will_come = ?,
            allergies = ?,
            allergies_details = ?,
            alcohol = ?,
            additional_info = ?,
            answered_at = ?
        WHERE id = ?
        """,
        (
            will_come,
            comment_will_come or "",
            None if allergies is None else int(allergies),
            allergies_details or "",
            None if alcohol is None else int(alcohol),
            additional_info or "",
            answered_at,
            response_id,
        ),
    )
    conn.commit()
    return get_response(response_id)


def delete_response(response_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM responses WHERE id = ?", (response_id,))
    conn.commit()
