"""
Report service — generate reports and export to CSV.
"""

import csv
import os
from datetime import date, datetime
from database.db import db
from utils.logger import logger
from utils.helpers import format_currency, format_date


def get_monthly_revenue_report(year: int = None, month: int = None) -> dict:
    """Generate monthly revenue report."""
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month

    month_str = f"{year}-{month:02d}"

    data = db.fetch_all(
        """SELECT m.name, m.phone, m.gender,
                  p.total_amount, p.paid_amount, p.pending_amount,
                  p.payment_mode, p.status, p.payment_date,
                  s.billing_date, s.next_due_date
           FROM payments p
           JOIN members m ON p.member_id = m.member_id
           JOIN subscriptions s ON p.subscription_id = s.subscription_id
           WHERE strftime('%Y-%m', s.billing_date) = ?
           OR strftime('%Y-%m', p.payment_date) = ?
           ORDER BY m.name ASC""",
        (month_str, month_str),
    )

    summary = db.fetch_one(
        """SELECT
               COALESCE(SUM(p.paid_amount), 0) as total_collected,
               COALESCE(SUM(p.pending_amount), 0) as total_pending,
               COUNT(DISTINCT p.member_id) as member_count
           FROM payments p
           JOIN subscriptions s ON p.subscription_id = s.subscription_id
           WHERE strftime('%Y-%m', s.billing_date) = ?
           OR strftime('%Y-%m', p.payment_date) = ?""",
        (month_str, month_str),
    )

    return {
        "year": year,
        "month": month,
        "data": data,
        "summary": summary or {"total_collected": 0, "total_pending": 0, "member_count": 0},
    }


def get_pending_payments_report() -> list:
    """Get all pending/partial payments."""
    return db.fetch_all(
        """SELECT m.name, m.phone, m.gender,
                  p.total_amount, p.paid_amount, p.pending_amount,
                  p.status, s.next_due_date,
                  julianday('now', 'localtime') - julianday(s.next_due_date) as days_overdue
           FROM payments p
           JOIN members m ON p.member_id = m.member_id
           JOIN subscriptions s ON p.subscription_id = s.subscription_id
           WHERE p.status IN ('Partial', 'Unpaid')
           AND m.status = 'Active'
           AND s.status = 'Active'
           ORDER BY s.next_due_date ASC"""
    )


def get_member_list_report(status: str = None) -> list:
    """Get member list for report."""
    query = """
        SELECT m.member_id, m.name, m.phone, m.gender, m.joining_date, m.status,
               s.fee, s.billing_date, s.next_due_date,
               COALESCE(p.paid_amount, 0) as last_paid,
               COALESCE(p.pending_amount, s.fee) as current_pending,
               COALESCE(p.status, 'Unpaid') as payment_status
        FROM members m
        LEFT JOIN subscriptions s ON m.member_id = s.member_id AND s.status = 'Active'
        LEFT JOIN payments p ON m.member_id = p.member_id
            AND p.subscription_id = s.subscription_id
    """
    params = []

    if status:
        query += " WHERE m.status = ?"
        params.append(status)

    query += " ORDER BY m.name ASC"

    return db.fetch_all(query, tuple(params))


def export_to_csv(data: list, filename: str, headers: list = None) -> str:
    """
    Export data to CSV file.
    Returns the file path.
    """
    if not data:
        logger.warning("No data to export")
        return ""

    # Create exports directory
    export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
    os.makedirs(export_dir, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(export_dir, f"{filename}_{timestamp}.csv")

    try:
        if not headers:
            headers = list(data[0].keys())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"CSV exported: {filepath} ({len(data)} rows)")
        return filepath
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return ""


def export_monthly_revenue_csv(year: int = None, month: int = None) -> str:
    """Export monthly revenue report to CSV."""
    report = get_monthly_revenue_report(year, month)
    if not report["data"]:
        return ""

    headers = [
        "name", "phone", "gender", "total_amount", "paid_amount",
        "pending_amount", "payment_mode", "status", "payment_date",
    ]
    return export_to_csv(report["data"], "monthly_revenue", headers)


def export_pending_payments_csv() -> str:
    """Export pending payments report to CSV."""
    data = get_pending_payments_report()
    headers = [
        "name", "phone", "gender", "total_amount", "paid_amount",
        "pending_amount", "status", "next_due_date", "days_overdue",
    ]
    return export_to_csv(data, "pending_payments", headers)


def export_member_list_csv(status: str = None) -> str:
    """Export member list to CSV."""
    data = get_member_list_report(status)
    headers = [
        "member_id", "name", "phone", "gender", "joining_date",
        "status", "fee", "current_pending", "payment_status",
    ]
    return export_to_csv(data, "member_list", headers)
