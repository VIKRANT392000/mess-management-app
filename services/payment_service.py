"""
Payment service — record payments, auto-calculate status and pending.
"""

from datetime import date
from database.db import db
from utils.logger import logger
from utils.validators import validate_payment_form
from utils.helpers import calc_payment_status, today_str


def create_initial_payment(member_id: int, subscription_id: int, total_amount: float) -> dict:
    """
    Create an initial unpaid payment record when subscription is created.
    """
    try:
        cursor = db.execute(
            """INSERT INTO payments
               (member_id, subscription_id, total_amount, paid_amount,
                pending_amount, payment_date, payment_mode, status)
               VALUES (?, ?, ?, 0, ?, ?, NULL, 'Unpaid')""",
            (member_id, subscription_id, total_amount, total_amount, today_str()),
        )
        logger.info(f"Initial payment record created for member {member_id}: Rs.{total_amount}")
        return {"success": True, "payment_id": cursor.lastrowid}
    except Exception as e:
        logger.error(f"Error creating initial payment: {e}")
        return {"success": False, "errors": {"general": str(e)}}


def record_payment(member_id: int, paid_amount_str: str, payment_mode: str, subscription_id: int = None) -> dict:
    """
    Record a payment for a member.
    Auto-calculates pending amount and status.
    """
    # Get active subscription if not provided
    if not subscription_id:
        sub = db.fetch_one(
            """SELECT subscription_id, fee FROM subscriptions
               WHERE member_id = ? AND status = 'Active'
               ORDER BY created_at DESC LIMIT 1""",
            (member_id,),
        )
        if not sub:
            return {"success": False, "errors": {"member": "No active subscription found"}}
        subscription_id = sub["subscription_id"]

    # Get existing payment record or total amount
    existing = db.fetch_one(
        """SELECT payment_id, total_amount, paid_amount, pending_amount
           FROM payments
           WHERE member_id = ? AND subscription_id = ?
           ORDER BY created_at DESC LIMIT 1""",
        (member_id, subscription_id),
    )

    if existing:
        total_amount = existing["total_amount"]
        already_paid = existing["paid_amount"]
    else:
        sub = db.fetch_one(
            "SELECT fee FROM subscriptions WHERE subscription_id = ?",
            (subscription_id,),
        )
        total_amount = sub["fee"] if sub else 0
        already_paid = 0

    remaining = total_amount - already_paid

    # Validate
    is_valid, errors, parsed_paid = validate_payment_form(
        member_id, paid_amount_str, remaining, payment_mode
    )
    if not is_valid:
        return {"success": False, "errors": errors}

    new_total_paid = already_paid + parsed_paid
    new_pending = total_amount - new_total_paid
    status = calc_payment_status(total_amount, new_total_paid)

    try:
        if existing:
            # Update existing payment record
            db.execute(
                """UPDATE payments
                   SET paid_amount = ?, pending_amount = ?, status = ?,
                       payment_mode = ?, payment_date = ?
                   WHERE payment_id = ?""",
                (new_total_paid, new_pending, status, payment_mode, today_str(), existing["payment_id"]),
            )
            payment_id = existing["payment_id"]
        else:
            # Create new payment record
            cursor = db.execute(
                """INSERT INTO payments
                   (member_id, subscription_id, total_amount, paid_amount,
                    pending_amount, payment_date, payment_mode, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (member_id, subscription_id, total_amount, parsed_paid,
                 total_amount - parsed_paid, today_str(), payment_mode, status),
            )
            payment_id = cursor.lastrowid

        logger.info(
            f"Payment recorded: member={member_id}, paid=Rs.{parsed_paid}, "
            f"total_paid=Rs.{new_total_paid}, pending=Rs.{new_pending}, status={status}"
        )
        return {
            "success": True,
            "payment_id": payment_id,
            "total_amount": total_amount,
            "paid_amount": new_total_paid,
            "pending_amount": new_pending,
            "status": status,
        }
    except Exception as e:
        logger.error(f"Error recording payment: {e}")
        return {"success": False, "errors": {"general": str(e)}}


def get_payment_info(member_id: int, subscription_id: int = None) -> dict:
    """Get current payment info for a member."""
    if subscription_id:
        return db.fetch_one(
            """SELECT p.*, m.name, m.phone, m.gender
               FROM payments p
               JOIN members m ON p.member_id = m.member_id
               WHERE p.member_id = ? AND p.subscription_id = ?
               ORDER BY p.created_at DESC LIMIT 1""",
            (member_id, subscription_id),
        )
    return db.fetch_one(
        """SELECT p.*, m.name, m.phone, m.gender, s.fee, s.next_due_date, s.billing_date
           FROM payments p
           JOIN members m ON p.member_id = m.member_id
           JOIN subscriptions s ON p.subscription_id = s.subscription_id
           WHERE p.member_id = ? AND s.status = 'Active'
           ORDER BY p.created_at DESC LIMIT 1""",
        (member_id,),
    )


def get_all_payments(
    status_filter: str = None,
    gender_filter: str = None,
    date_from: str = None,
    date_to: str = None,
    search: str = None,
) -> list:
    """Get all payments with optional filters."""
    query = """
        SELECT p.*, m.name, m.phone, m.gender,
               s.billing_date, s.next_due_date
        FROM payments p
        JOIN members m ON p.member_id = m.member_id
        JOIN subscriptions s ON p.subscription_id = s.subscription_id
        WHERE m.status = 'Active'
    """
    params = []

    if status_filter:
        query += " AND p.status = ?"
        params.append(status_filter)

    if gender_filter:
        query += " AND m.gender = ?"
        params.append(gender_filter)

    if date_from:
        query += " AND p.payment_date >= ?"
        params.append(date_from)

    if date_to:
        query += " AND p.payment_date <= ?"
        params.append(date_to)

    if search:
        query += " AND (m.name LIKE ? OR m.phone LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term])

    query += " ORDER BY p.payment_date DESC"

    return db.fetch_all(query, tuple(params))


def get_due_today() -> list:
    """Get members with payment due today."""
    return db.fetch_all(
        """SELECT p.*, m.name, m.phone, m.gender, s.next_due_date
           FROM payments p
           JOIN members m ON p.member_id = m.member_id
           JOIN subscriptions s ON p.subscription_id = s.subscription_id
           WHERE s.next_due_date = date('now', 'localtime')
           AND s.status = 'Active'
           AND p.status != 'Paid'
           AND m.status = 'Active'"""
    )


def get_overdue() -> list:
    """Get overdue payments."""
    return db.fetch_all(
        """SELECT p.*, m.name, m.phone, m.gender, s.next_due_date
           FROM payments p
           JOIN members m ON p.member_id = m.member_id
           JOIN subscriptions s ON p.subscription_id = s.subscription_id
           WHERE s.next_due_date < date('now', 'localtime')
           AND s.status = 'Active'
           AND p.status != 'Paid'
           AND m.status = 'Active'
           ORDER BY s.next_due_date ASC"""
    )


def get_paid_this_month() -> list:
    """Get payments made this month."""
    return db.fetch_all(
        """SELECT p.*, m.name, m.phone, m.gender
           FROM payments p
           JOIN members m ON p.member_id = m.member_id
           WHERE p.status = 'Paid'
           AND strftime('%Y-%m', p.payment_date) = strftime('%Y-%m', 'now', 'localtime')
           AND m.status = 'Active'
           ORDER BY p.payment_date DESC"""
    )


def get_revenue_summary() -> dict:
    """Get total revenue and pending summary."""
    result = db.fetch_one("""
        SELECT
            COALESCE(SUM(p.paid_amount), 0) as total_revenue,
            COALESCE(SUM(p.pending_amount), 0) as total_pending,
            COUNT(*) as total_payments,
            SUM(CASE WHEN p.status = 'Paid' THEN 1 ELSE 0 END) as paid_count,
            SUM(CASE WHEN p.status = 'Partial' THEN 1 ELSE 0 END) as partial_count,
            SUM(CASE WHEN p.status = 'Unpaid' THEN 1 ELSE 0 END) as unpaid_count
        FROM payments p
        JOIN members m ON p.member_id = m.member_id
        WHERE m.status = 'Active'
    """)
    return result or {
        "total_revenue": 0, "total_pending": 0, "total_payments": 0,
        "paid_count": 0, "partial_count": 0, "unpaid_count": 0,
    }


def get_calendar_data(year: int, month: int) -> list:
    """Get payment data for calendar view (grouped by day)."""
    month_str = f"{year}-{month:02d}"
    return db.fetch_all(
        """SELECT
               CAST(strftime('%d', s.next_due_date) AS INTEGER) as day,
               p.status,
               COUNT(*) as count
           FROM payments p
           JOIN subscriptions s ON p.subscription_id = s.subscription_id
           JOIN members m ON p.member_id = m.member_id
           WHERE strftime('%Y-%m', s.next_due_date) = ?
           AND m.status = 'Active'
           GROUP BY day, p.status""",
        (month_str,),
    )
