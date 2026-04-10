"""
Subscription service — auto fee assignment and billing cycle management.
"""

from datetime import date, timedelta
from database.db import db
from utils.logger import logger
from utils.constants import MALE_FEE, FEMALE_FEE, BILLING_CYCLE_DAYS
from utils.helpers import calc_next_due_date, get_fee_for_gender


def create_subscription(member_id: int, gender: str, billing_date: str = None) -> dict:
    """
    Create a new subscription for a member.
    Auto-assigns fee based on gender and calculates next_due_date.
    """
    if not billing_date:
        billing_date = date.today().isoformat()

    fee = get_fee_for_gender(gender)
    next_due = calc_next_due_date(billing_date, BILLING_CYCLE_DAYS)

    if not next_due:
        return {"success": False, "errors": {"billing_date": "Invalid billing date"}}

    try:
        # Deactivate any existing active subscription
        db.execute(
            """UPDATE subscriptions SET status = 'Expired'
               WHERE member_id = ? AND status = 'Active'""",
            (member_id,),
        )

        cursor = db.execute(
            """INSERT INTO subscriptions (member_id, fee, billing_date, next_due_date)
               VALUES (?, ?, ?, ?)""",
            (member_id, fee, billing_date, next_due),
        )
        sub_id = cursor.lastrowid
        logger.info(
            f"Subscription created: member={member_id}, fee=Rs.{fee}, "
            f"billing={billing_date}, due={next_due}"
        )
        return {"success": True, "subscription_id": sub_id, "fee": fee, "next_due_date": next_due}
    except Exception as e:
        logger.error(f"Error creating subscription for member {member_id}: {e}")
        return {"success": False, "errors": {"general": str(e)}}


def get_active_subscription(member_id: int) -> dict:
    """Get the active subscription for a member."""
    return db.fetch_one(
        """SELECT * FROM subscriptions
           WHERE member_id = ? AND status = 'Active'
           ORDER BY created_at DESC LIMIT 1""",
        (member_id,),
    )


def get_subscription_by_id(subscription_id: int) -> dict:
    """Get subscription by ID."""
    return db.fetch_one(
        "SELECT * FROM subscriptions WHERE subscription_id = ?",
        (subscription_id,),
    )


def renew_subscription(member_id: int, carry_forward_pending: float = 0) -> dict:
    """
    Renew subscription for next cycle.
    Optionally carry forward pending amount.
    """
    # Get member gender for fee
    member = db.fetch_one(
        "SELECT gender FROM members WHERE member_id = ?", (member_id,)
    )
    if not member:
        return {"success": False, "errors": {"member": "Member not found"}}

    today_iso = date.today().isoformat()
    result = create_subscription(member_id, member["gender"], today_iso)

    if result["success"] and carry_forward_pending > 0:
        # The payment service will handle carry-forward
        logger.info(
            f"Subscription renewed for member {member_id} with "
            f"Rs.{carry_forward_pending} carry-forward"
        )

    return result


def get_expired_subscriptions() -> list:
    """Get subscriptions whose due date has passed and are still Active."""
    today_iso = date.today().isoformat()
    return db.fetch_all(
        """SELECT s.*, m.name, m.gender, m.phone
           FROM subscriptions s
           JOIN members m ON s.member_id = m.member_id
           WHERE s.status = 'Active'
           AND s.next_due_date < ?
           AND m.status = 'Active'""",
        (today_iso,),
    )


def auto_cycle_subscriptions():
    """
    Monthly auto-cycle:
    Check for expired subscriptions, renew them, and carry forward pending.
    Called on app startup.
    """
    expired = get_expired_subscriptions()

    if not expired:
        logger.info("No expired subscriptions to cycle")
        return 0

    count = 0
    for sub in expired:
        member_id = sub["member_id"]

        # Get pending amount from payments for this subscription
        pending_data = db.fetch_one(
            """SELECT COALESCE(SUM(pending_amount), 0) as total_pending
               FROM payments
               WHERE subscription_id = ? AND status != 'Paid'""",
            (sub["subscription_id"],),
        )
        pending = pending_data["total_pending"] if pending_data else 0

        # Mark old subscription as expired
        db.execute(
            "UPDATE subscriptions SET status = 'Expired' WHERE subscription_id = ?",
            (sub["subscription_id"],),
        )

        # Create new subscription
        result = renew_subscription(member_id, pending)
        if result["success"]:
            # Create new unpaid payment record with carry-forward
            new_fee = result["fee"]
            total_with_carry = new_fee + pending

            from services.payment_service import create_initial_payment
            create_initial_payment(
                member_id, result["subscription_id"], total_with_carry
            )
            count += 1
            logger.info(
                f"Auto-cycled: member {member_id}, "
                f"new total=Rs.{total_with_carry} (fee=Rs.{new_fee} + pending=Rs.{pending})"
            )

    logger.info(f"Auto-cycle complete: {count} subscriptions renewed")
    return count
