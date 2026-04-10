"""
Reminder service — upcoming, due today, and overdue reminders.
"""

from database.db import db
from utils.logger import logger


def get_upcoming_reminders(days: int = 2) -> list:
    """Get members with dues in the next N days (excluding today)."""
    return db.fetch_all(
        """SELECT m.member_id, m.name, m.phone, m.gender,
                  s.next_due_date, s.fee,
                  COALESCE(p.pending_amount, s.fee) as pending_amount,
                  'Upcoming' as reminder_type
           FROM members m
           JOIN subscriptions s ON m.member_id = s.member_id AND s.status = 'Active'
           LEFT JOIN payments p ON p.member_id = m.member_id
               AND p.subscription_id = s.subscription_id
           WHERE m.status = 'Active'
           AND s.next_due_date > date('now', 'localtime')
           AND s.next_due_date <= date('now', 'localtime', '+' || ? || ' days')
           AND (p.status IS NULL OR p.status != 'Paid')
           ORDER BY s.next_due_date ASC""",
        (str(days),),
    )


def get_due_today_reminders() -> list:
    """Get members with dues today."""
    return db.fetch_all(
        """SELECT m.member_id, m.name, m.phone, m.gender,
                  s.next_due_date, s.fee,
                  COALESCE(p.pending_amount, s.fee) as pending_amount,
                  'Due Today' as reminder_type
           FROM members m
           JOIN subscriptions s ON m.member_id = s.member_id AND s.status = 'Active'
           LEFT JOIN payments p ON p.member_id = m.member_id
               AND p.subscription_id = s.subscription_id
           WHERE m.status = 'Active'
           AND s.next_due_date = date('now', 'localtime')
           AND (p.status IS NULL OR p.status != 'Paid')
           ORDER BY m.name ASC"""
    )


def get_overdue_reminders() -> list:
    """Get members with overdue payments."""
    return db.fetch_all(
        """SELECT m.member_id, m.name, m.phone, m.gender,
                  s.next_due_date, s.fee,
                  COALESCE(p.pending_amount, s.fee) as pending_amount,
                  'Overdue' as reminder_type
           FROM members m
           JOIN subscriptions s ON m.member_id = s.member_id AND s.status = 'Active'
           LEFT JOIN payments p ON p.member_id = m.member_id
               AND p.subscription_id = s.subscription_id
           WHERE m.status = 'Active'
           AND s.next_due_date < date('now', 'localtime')
           AND (p.status IS NULL OR p.status != 'Paid')
           ORDER BY s.next_due_date ASC"""
    )


def get_all_reminders() -> dict:
    """Get all reminders grouped by type."""
    return {
        "upcoming": get_upcoming_reminders(),
        "due_today": get_due_today_reminders(),
        "overdue": get_overdue_reminders(),
    }


def get_dashboard_reminders(days: int = 3) -> list:
    """Get reminders for dashboard widget (upcoming + overdue, limited)."""
    upcoming = get_upcoming_reminders(days)
    due_today = get_due_today_reminders()
    overdue = get_overdue_reminders()

    # Combine and limit
    all_reminders = overdue + due_today + upcoming
    return all_reminders[:10]  # Limit for dashboard


def get_reminder_counts() -> dict:
    """Get reminder counts for badge display."""
    upcoming = len(get_upcoming_reminders())
    due_today = len(get_due_today_reminders())
    overdue = len(get_overdue_reminders())

    return {
        "upcoming": upcoming,
        "due_today": due_today,
        "overdue": overdue,
        "total": upcoming + due_today + overdue,
    }
