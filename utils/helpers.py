"""
Helper utilities for the Mess Management System.
"""

from datetime import datetime, timedelta, date


def format_currency(amount: float) -> str:
    """Format amount as Indian Rupees."""
    if amount is None:
        return "Rs.0.00"
    return f"Rs.{amount:,.2f}"


def format_date(date_str: str, output_format: str = "%d %b %Y") -> str:
    """Convert YYYY-MM-DD to human-readable format (e.g., '10 Apr 2026')."""
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
        return dt.strftime(output_format)
    except (ValueError, TypeError):
        return str(date_str)


def format_date_short(date_str: str) -> str:
    """Convert to short format (e.g., '10 Apr')."""
    return format_date(date_str, "%d %b")


def today_str() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return date.today().strftime("%Y-%m-%d")


def calc_next_due_date(billing_date: str, cycle_days: int = 30) -> str:
    """Calculate next due date by adding cycle days to billing date."""
    try:
        dt = datetime.strptime(str(billing_date).strip(), "%Y-%m-%d")
        next_due = dt + timedelta(days=cycle_days)
        return next_due.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""


def days_until_due(due_date_str: str) -> int:
    """
    Calculate days until due date.
    Negative = overdue, 0 = due today, positive = upcoming.
    """
    try:
        due = datetime.strptime(str(due_date_str).strip(), "%Y-%m-%d").date()
        return (due - date.today()).days
    except (ValueError, TypeError):
        return 0


def get_reminder_type(due_date_str: str) -> str:
    """Determine reminder type based on due date."""
    days = days_until_due(due_date_str)
    if days < 0:
        return "Overdue"
    elif days == 0:
        return "Due Today"
    elif days <= 2:
        return "Upcoming"
    else:
        return "Normal"


def get_fee_for_gender(gender: str) -> float:
    """Return subscription fee based on gender."""
    from utils.constants import MALE_FEE, FEMALE_FEE
    return MALE_FEE if gender == "Male" else FEMALE_FEE


def calc_payment_status(total: float, paid: float) -> str:
    """Determine payment status based on amounts."""
    if paid <= 0:
        return "Unpaid"
    elif paid >= total:
        return "Paid"
    else:
        return "Partial"


def get_month_name(month: int) -> str:
    """Return month name from number (1-12)."""
    months = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if 1 <= month <= 12:
        return months[month]
    return ""


def get_days_in_month(year: int, month: int) -> int:
    """Return number of days in a given month."""
    import calendar
    return calendar.monthrange(year, month)[1]


def get_first_weekday(year: int, month: int) -> int:
    """Return weekday of the first day (0=Monday, 6=Sunday)."""
    return date(year, month, 1).weekday()


def truncate_text(text: str, max_length: int = 20) -> str:
    """Truncate text with ellipsis if too long."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
