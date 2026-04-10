"""
Constants and configuration for the Mess Management System.
"""

# ─── Fee Configuration ───
MALE_FEE = 2200.0
FEMALE_FEE = 1800.0
BILLING_CYCLE_DAYS = 30
REMINDER_UPCOMING_DAYS = 2
REMINDER_DASHBOARD_DAYS = 3

# ─── Status Enums ───
STATUS_ACTIVE = "Active"
STATUS_INACTIVE = "Inactive"

PAYMENT_PAID = "Paid"
PAYMENT_PARTIAL = "Partial"
PAYMENT_UNPAID = "Unpaid"

GENDER_MALE = "Male"
GENDER_FEMALE = "Female"

PAYMENT_MODES = ["Cash", "UPI", "Bank"]
GENDERS = [GENDER_MALE, GENDER_FEMALE]
MEMBER_STATUSES = [STATUS_ACTIVE, STATUS_INACTIVE]
PAYMENT_STATUSES = [PAYMENT_PAID, PAYMENT_PARTIAL, PAYMENT_UNPAID]

# ─── Color Palette (RGBA for Kivy) ───
COLORS = {
    "primary": (0.102, 0.137, 0.494, 1),        # #1A237E Deep Blue
    "primary_light": (0.224, 0.286, 0.671, 1),   # #3949AB Indigo
    "accent": (1.0, 0.702, 0.0, 1),              # #FFB300 Amber
    "success": (0.180, 0.490, 0.196, 1),          # #2E7D32 Green
    "warning": (0.961, 0.498, 0.090, 1),          # #F57F17 Orange
    "danger": (0.776, 0.157, 0.157, 1),           # #C62828 Red
    "bg": (0.960, 0.960, 0.960, 1),               # #F5F5F5 Light Gray
    "card_bg": (1.0, 1.0, 1.0, 1),                # #FFFFFF White
    "text_primary": (0.129, 0.129, 0.129, 1),     # #212121 Dark Gray
    "text_secondary": (0.459, 0.459, 0.459, 1),   # #757575 Medium Gray
    "divider": (0.878, 0.878, 0.878, 1),           # #E0E0E0
    "nav_bg": (0.102, 0.137, 0.494, 1),           # #1A237E
    "white": (1, 1, 1, 1),
    "black": (0, 0, 0, 1),
    "transparent": (0, 0, 0, 0),
}

# Hex colors for KV files
HEX_COLORS = {
    "primary": "#1A237E",
    "primary_light": "#3949AB",
    "accent": "#FFB300",
    "success": "#2E7D32",
    "success_light": "#E8F5E9",
    "warning": "#F57F17",
    "warning_light": "#FFF8E1",
    "danger": "#C62828",
    "danger_light": "#FFEBEE",
    "bg": "#F5F5F5",
    "card_bg": "#FFFFFF",
    "text_primary": "#212121",
    "text_secondary": "#757575",
    "divider": "#E0E0E0",
    "white": "#FFFFFF",
}

# ─── Database ───
DB_NAME = "mess_management.db"

# ─── App Info ───
APP_NAME = "Mess Manager"
APP_VERSION = "1.0.0"
