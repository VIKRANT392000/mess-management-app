"""
Database models — table creation and sample data seeding.
"""

from datetime import date, timedelta
import random
from database.db import db
from utils.logger import logger
from utils.constants import MALE_FEE, FEMALE_FEE, BILLING_CYCLE_DAYS


def create_tables():
    """Create all database tables if they don't exist."""
    logger.info("Creating database tables...")

    # Members table
    db.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female')),
            joining_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Inactive')),
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # Subscriptions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            fee REAL NOT NULL,
            billing_date TEXT NOT NULL,
            next_due_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Expired', 'Cancelled')),
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE
        )
    """)

    # Payments table
    db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            subscription_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            paid_amount REAL NOT NULL DEFAULT 0 CHECK(paid_amount >= 0),
            pending_amount REAL NOT NULL DEFAULT 0,
            payment_date TEXT NOT NULL,
            payment_mode TEXT CHECK(payment_mode IN ('Cash', 'UPI', 'Bank')),
            status TEXT NOT NULL DEFAULT 'Unpaid' CHECK(status IN ('Paid', 'Partial', 'Unpaid')),
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id) ON DELETE CASCADE
        )
    """)

    # Create indexes for performance
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_members_phone ON members(phone)
    """)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)
    """)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_member ON subscriptions(member_id)
    """)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscriptions_due ON subscriptions(next_due_date)
    """)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_member ON payments(member_id)
    """)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)
    """)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date)
    """)

    # Create reminder view
    db.execute("""
        CREATE VIEW IF NOT EXISTS v_reminders AS
        SELECT
            m.member_id,
            m.name AS member_name,
            m.phone,
            s.next_due_date AS due_date,
            s.fee,
            COALESCE(p.pending_amount, s.fee) AS pending_amount,
            CASE
                WHEN s.next_due_date < date('now', 'localtime') THEN 'Overdue'
                WHEN s.next_due_date = date('now', 'localtime') THEN 'Due Today'
                WHEN s.next_due_date <= date('now', 'localtime', '+2 days') THEN 'Upcoming'
                ELSE 'Normal'
            END AS reminder_type
        FROM members m
        JOIN subscriptions s ON m.member_id = s.member_id AND s.status = 'Active'
        LEFT JOIN (
            SELECT member_id, subscription_id,
                   SUM(paid_amount) as total_paid,
                   MAX(total_amount) - SUM(paid_amount) as pending_amount
            FROM payments
            GROUP BY member_id, subscription_id
        ) p ON s.member_id = p.member_id AND s.subscription_id = p.subscription_id
        WHERE m.status = 'Active'
        AND s.next_due_date <= date('now', 'localtime', '+3 days')
    """)

    logger.info("All tables and views created successfully")


def seed_sample_data():
    """Insert sample data for demo purposes."""
    # Check if data already exists
    existing = db.fetch_one("SELECT COUNT(*) as cnt FROM members")
    if existing and existing["cnt"] > 0:
        logger.info("Sample data already exists, skipping seed")
        return

    logger.info("Seeding sample data...")

    today = date.today()

    # Sample members
    members = [
        ("Rahul Sharma", "9876543210", "Male", (today - timedelta(days=60)).isoformat()),
        ("Priya Patel", "9876543211", "Female", (today - timedelta(days=45)).isoformat()),
        ("Amit Kumar", "9876543212", "Male", (today - timedelta(days=30)).isoformat()),
        ("Sneha Gupta", "9876543213", "Female", (today - timedelta(days=25)).isoformat()),
        ("Vikram Singh", "9876543214", "Male", (today - timedelta(days=20)).isoformat()),
        ("Anita Desai", "9876543215", "Female", (today - timedelta(days=15)).isoformat()),
        ("Rajesh Verma", "9876543216", "Male", (today - timedelta(days=10)).isoformat()),
        ("Kavita Nair", "9876543217", "Female", (today - timedelta(days=8)).isoformat()),
        ("Suresh Reddy", "9876543218", "Male", (today - timedelta(days=5)).isoformat()),
        ("Meera Joshi", "9876543219", "Female", (today - timedelta(days=3)).isoformat()),
    ]

    for name, phone, gender, joining_date in members:
        # Insert member
        cursor = db.execute(
            "INSERT INTO members (name, phone, gender, joining_date) VALUES (?, ?, ?, ?)",
            (name, phone, gender, joining_date),
        )
        member_id = cursor.lastrowid

        # Create subscription
        fee = MALE_FEE if gender == "Male" else FEMALE_FEE
        billing_date = joining_date
        next_due = (
            date.fromisoformat(billing_date) + timedelta(days=BILLING_CYCLE_DAYS)
        ).isoformat()

        cursor = db.execute(
            "INSERT INTO subscriptions (member_id, fee, billing_date, next_due_date) VALUES (?, ?, ?, ?)",
            (member_id, fee, billing_date, next_due),
        )
        sub_id = cursor.lastrowid

        # Create varied payment records
        payment_scenarios = [
            ("Paid", fee, fee, 0),
            ("Partial", fee, fee * 0.5, fee * 0.5),
            ("Unpaid", fee, 0, fee),
        ]
        scenario = random.choice(payment_scenarios)
        status, total, paid, pending = scenario
        mode = random.choice(["Cash", "UPI", "Bank"])

        payment_date = (
            date.fromisoformat(billing_date) + timedelta(days=random.randint(1, 10))
        ).isoformat()

        db.execute(
            """INSERT INTO payments
               (member_id, subscription_id, total_amount, paid_amount, pending_amount,
                payment_date, payment_mode, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (member_id, sub_id, total, paid, pending, payment_date, mode, status),
        )

    logger.info("Sample data seeded: 10 members with subscriptions and payments")


def reset_database():
    """Drop all tables and recreate (for development only)."""
    logger.warning("Resetting database — all data will be lost!")
    db.execute("DROP VIEW IF EXISTS v_reminders")
    db.execute("DROP TABLE IF EXISTS payments")
    db.execute("DROP TABLE IF EXISTS subscriptions")
    db.execute("DROP TABLE IF EXISTS members")
    create_tables()
    logger.info("Database reset complete")
