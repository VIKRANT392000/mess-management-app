"""
Member service — CRUD operations for members.
"""

from database.db import db
from utils.logger import logger
from utils.validators import validate_member_form, validate_phone
from utils.helpers import today_str


def add_member(name: str, phone: str, gender: str, joining_date: str) -> dict:
    """
    Add a new member.
    Returns dict with 'success', 'member_id' or 'errors'.
    """
    # Validate form
    is_valid, errors = validate_member_form(name, phone, gender, joining_date)
    if not is_valid:
        return {"success": False, "errors": errors}

    # Check phone uniqueness
    existing = db.fetch_one(
        "SELECT member_id FROM members WHERE phone = ?", (phone.strip(),)
    )
    if existing:
        return {"success": False, "errors": {"phone": "Phone number already registered"}}

    try:
        cursor = db.execute(
            """INSERT INTO members (name, phone, gender, joining_date)
               VALUES (?, ?, ?, ?)""",
            (name.strip(), phone.strip(), gender, joining_date.strip()),
        )
        member_id = cursor.lastrowid
        logger.info(f"Member added: {name} (ID: {member_id})")
        return {"success": True, "member_id": member_id}
    except Exception as e:
        logger.error(f"Error adding member: {e}")
        return {"success": False, "errors": {"general": str(e)}}


def edit_member(member_id: int, name: str, phone: str, gender: str, joining_date: str) -> dict:
    """
    Edit an existing member.
    Returns dict with 'success' or 'errors'.
    """
    is_valid, errors = validate_member_form(name, phone, gender, joining_date)
    if not is_valid:
        return {"success": False, "errors": errors}

    # Check phone uniqueness (exclude current member)
    existing = db.fetch_one(
        "SELECT member_id FROM members WHERE phone = ? AND member_id != ?",
        (phone.strip(), member_id),
    )
    if existing:
        return {"success": False, "errors": {"phone": "Phone number already in use by another member"}}

    try:
        db.execute(
            """UPDATE members
               SET name = ?, phone = ?, gender = ?, joining_date = ?,
                   updated_at = datetime('now', 'localtime')
               WHERE member_id = ?""",
            (name.strip(), phone.strip(), gender, joining_date.strip(), member_id),
        )
        logger.info(f"Member updated: ID {member_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error editing member {member_id}: {e}")
        return {"success": False, "errors": {"general": str(e)}}


def delete_member(member_id: int) -> dict:
    """
    Soft delete a member (set status to Inactive).
    """
    try:
        db.execute(
            """UPDATE members
               SET status = 'Inactive', updated_at = datetime('now', 'localtime')
               WHERE member_id = ?""",
            (member_id,),
        )
        # Also deactivate subscriptions
        db.execute(
            """UPDATE subscriptions SET status = 'Cancelled'
               WHERE member_id = ? AND status = 'Active'""",
            (member_id,),
        )
        logger.info(f"Member soft-deleted: ID {member_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error deleting member {member_id}: {e}")
        return {"success": False, "errors": {"general": str(e)}}


def reactivate_member(member_id: int) -> dict:
    """Reactivate a member."""
    try:
        db.execute(
            """UPDATE members
               SET status = 'Active', updated_at = datetime('now', 'localtime')
               WHERE member_id = ?""",
            (member_id,),
        )
        logger.info(f"Member reactivated: ID {member_id}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Error reactivating member {member_id}: {e}")
        return {"success": False, "errors": {"general": str(e)}}


def get_all_members(status_filter: str = None, gender_filter: str = None, search: str = None) -> list:
    """
    Get all members with optional filters.
    """
    query = "SELECT * FROM members WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if gender_filter:
        query += " AND gender = ?"
        params.append(gender_filter)

    if search:
        query += " AND (name LIKE ? OR phone LIKE ?)"
        search_term = f"%{search.strip()}%"
        params.extend([search_term, search_term])

    query += " ORDER BY name ASC"

    return db.fetch_all(query, tuple(params))


def get_member_by_id(member_id: int) -> dict:
    """Get a single member by ID."""
    return db.fetch_one("SELECT * FROM members WHERE member_id = ?", (member_id,))


def get_member_by_phone(phone: str) -> dict:
    """Get a single member by phone."""
    return db.fetch_one("SELECT * FROM members WHERE phone = ?", (phone.strip(),))


def get_active_members() -> list:
    """Get only active members."""
    return get_all_members(status_filter="Active")


def get_member_count() -> dict:
    """Get member counts."""
    result = db.fetch_one("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN gender = 'Male' AND status = 'Active' THEN 1 ELSE 0 END) as male,
            SUM(CASE WHEN gender = 'Female' AND status = 'Active' THEN 1 ELSE 0 END) as female
        FROM members
    """)
    return result or {"total": 0, "active": 0, "male": 0, "female": 0}
