"""
Validation utilities for the Mess Management System.
"""

import re
from datetime import datetime


def validate_phone(phone: str) -> tuple:
    """
    Validate phone number.
    Returns (is_valid: bool, error_message: str)
    """
    if not phone or not phone.strip():
        return False, "Phone number is required"

    phone = phone.strip()

    if not re.match(r"^\d{10}$", phone):
        return False, "Phone must be exactly 10 digits"

    return True, ""


def validate_name(name: str) -> tuple:
    """
    Validate member name.
    Returns (is_valid: bool, error_message: str)
    """
    if not name or not name.strip():
        return False, "Name is required"

    name = name.strip()

    if len(name) < 2:
        return False, "Name must be at least 2 characters"

    if len(name) > 100:
        return False, "Name must be under 100 characters"

    if not re.match(r"^[a-zA-Z\s.'-]+$", name):
        return False, "Name can only contain letters, spaces, dots, hyphens"

    return True, ""


def validate_gender(gender: str) -> tuple:
    """
    Validate gender selection.
    Returns (is_valid: bool, error_message: str)
    """
    if not gender or gender not in ("Male", "Female"):
        return False, "Please select a valid gender (Male/Female)"
    return True, ""


def validate_date(date_str: str) -> tuple:
    """
    Validate date string in YYYY-MM-DD format.
    Returns (is_valid: bool, error_message: str)
    """
    if not date_str or not date_str.strip():
        return False, "Date is required"

    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"


def validate_amount(amount_str: str, max_amount: float = None) -> tuple:
    """
    Validate payment amount.
    Returns (is_valid: bool, error_message: str, parsed_amount: float)
    """
    if not amount_str or not str(amount_str).strip():
        return False, "Amount is required", 0.0

    try:
        amount = float(str(amount_str).strip())
    except (ValueError, TypeError):
        return False, "Amount must be a valid number", 0.0

    if amount < 0:
        return False, "Amount cannot be negative", 0.0

    if max_amount is not None and amount > max_amount:
        return False, f"Amount cannot exceed Rs.{max_amount:.2f}", 0.0

    return True, "", amount


def validate_payment_mode(mode: str) -> tuple:
    """
    Validate payment mode.
    Returns (is_valid: bool, error_message: str)
    """
    valid_modes = ("Cash", "UPI", "Bank")
    if not mode or mode not in valid_modes:
        return False, f"Please select a valid payment mode ({', '.join(valid_modes)})"
    return True, ""


def validate_member_form(name: str, phone: str, gender: str, date_str: str) -> tuple:
    """
    Validate the entire member form.
    Returns (is_valid: bool, errors: dict)
    """
    errors = {}

    valid, msg = validate_name(name)
    if not valid:
        errors["name"] = msg

    valid, msg = validate_phone(phone)
    if not valid:
        errors["phone"] = msg

    valid, msg = validate_gender(gender)
    if not valid:
        errors["gender"] = msg

    valid, msg = validate_date(date_str)
    if not valid:
        errors["joining_date"] = msg

    return len(errors) == 0, errors


def validate_payment_form(
    member_id, paid_amount: str, total_amount: float, payment_mode: str
) -> tuple:
    """
    Validate the entire payment form.
    Returns (is_valid: bool, errors: dict, parsed_paid: float)
    """
    errors = {}
    parsed_paid = 0.0

    if not member_id:
        errors["member"] = "Please select a member"

    valid, msg, parsed_paid = validate_amount(paid_amount, max_amount=total_amount)
    if not valid:
        errors["paid_amount"] = msg

    valid, msg = validate_payment_mode(payment_mode)
    if not valid:
        errors["payment_mode"] = msg

    return len(errors) == 0, errors, parsed_paid
