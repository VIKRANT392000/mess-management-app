"""
Receipt service — generate PDF receipts.
"""

import os
from datetime import datetime
from utils.logger import logger
from utils.helpers import format_currency, format_date


def generate_receipt_text(name: str, phone: str, amount_paid: float,
                          total_amount: float, payment_date: str,
                          payment_mode: str, remaining: float) -> str:
    """Generate a formatted text receipt."""
    receipt = f"""
╔══════════════════════════════════════════╗
║           MESS MANAGER RECEIPT           ║
╠══════════════════════════════════════════╣
║                                          ║
║  Receipt No:  RCP-{datetime.now().strftime('%Y%m%d%H%M%S')}       ║
║  Date:        {format_date(payment_date):<26}║
║                                          ║
╠══════════════════════════════════════════╣
║  MEMBER DETAILS                          ║
║  Name:        {name:<26}║
║  Phone:       {phone:<26}║
║                                          ║
╠══════════════════════════════════════════╣
║  PAYMENT DETAILS                         ║
║  Total Amount:   {format_currency(total_amount):<23}║
║  Amount Paid:    {format_currency(amount_paid):<23}║
║  Balance Due:    {format_currency(remaining):<23}║
║  Payment Mode:   {payment_mode:<23}║
║                                          ║
╠══════════════════════════════════════════╣
║  Status: {'PAID IN FULL' if remaining <= 0 else 'PARTIAL PAYMENT':<31}║
║                                          ║
║  Thank you for your payment!             ║
╚══════════════════════════════════════════╝
"""
    return receipt


def generate_receipt_pdf(name: str, phone: str, amount_paid: float,
                         total_amount: float, payment_date: str,
                         payment_mode: str, remaining: float) -> str:
    """
    Generate a PDF receipt using ReportLab.
    Returns the file path.
    """
    try:
        from reportlab.lib.pagesizes import A5
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor
        from reportlab.pdfgen import canvas
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        logger.warning("ReportLab not installed, falling back to text receipt")
        return save_text_receipt(name, phone, amount_paid, total_amount,
                                 payment_date, payment_mode, remaining)

    # Create receipts directory
    receipt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "receipts")
    os.makedirs(receipt_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"receipt_{name.replace(' ', '_')}_{timestamp}.pdf"
    filepath = os.path.join(receipt_dir, filename)

    try:
        c = canvas.Canvas(filepath, pagesize=A5)
        width, height = A5

        # Colors
        primary = HexColor("#1A237E")
        accent = HexColor("#FFB300")
        success = HexColor("#2E7D32")
        danger = HexColor("#C62828")
        gray = HexColor("#757575")
        light_gray = HexColor("#F5F5F5")

        # Header background
        c.setFillColor(primary)
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)

        # Header text
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 35, "MESS MANAGER")
        c.setFont("Helvetica", 11)
        c.drawCentredString(width / 2, height - 55, "Payment Receipt")

        # Receipt number and date
        receipt_no = f"RCP-{timestamp}"
        y = height - 100
        c.setFillColor(gray)
        c.setFont("Helvetica", 9)
        c.drawString(20, y, f"Receipt #: {receipt_no}")
        c.drawRightString(width - 20, y, f"Date: {format_date(payment_date)}")

        # Divider
        y -= 15
        c.setStrokeColor(HexColor("#E0E0E0"))
        c.line(20, y, width - 20, y)

        # Member details
        y -= 25
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20, y, "Member Details")

        y -= 20
        c.setFillColor(HexColor("#212121"))
        c.setFont("Helvetica", 10)
        c.drawString(20, y, f"Name:")
        c.drawString(100, y, name)

        y -= 18
        c.drawString(20, y, f"Phone:")
        c.drawString(100, y, phone)

        # Divider
        y -= 15
        c.line(20, y, width - 20, y)

        # Payment details
        y -= 25
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20, y, "Payment Details")

        details = [
            ("Total Amount:", format_currency(total_amount)),
            ("Amount Paid:", format_currency(amount_paid)),
            ("Balance Due:", format_currency(remaining)),
            ("Payment Mode:", payment_mode or "N/A"),
        ]

        for label, value in details:
            y -= 20
            c.setFillColor(HexColor("#212121"))
            c.setFont("Helvetica", 10)
            c.drawString(20, y, label)
            if "Balance" in label and remaining > 0:
                c.setFillColor(danger)
            elif "Paid" in label:
                c.setFillColor(success)
            c.setFont("Helvetica-Bold", 10)
            c.drawRightString(width - 20, y, value)

        # Status box
        y -= 35
        status_text = "PAID IN FULL" if remaining <= 0 else "PARTIAL PAYMENT"
        status_color = success if remaining <= 0 else HexColor("#F57F17")
        c.setFillColor(status_color)
        c.roundRect(20, y - 5, width - 40, 25, 5, fill=True, stroke=False)
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2, y + 3, status_text)

        # Footer
        y -= 40
        c.setFillColor(gray)
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, y, "Thank you for your payment!")
        c.drawCentredString(width / 2, y - 12, "This is a computer-generated receipt.")

        c.save()
        logger.info(f"PDF receipt generated: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Error generating PDF receipt: {e}")
        return save_text_receipt(name, phone, amount_paid, total_amount,
                                 payment_date, payment_mode, remaining)


def save_text_receipt(name: str, phone: str, amount_paid: float,
                      total_amount: float, payment_date: str,
                      payment_mode: str, remaining: float) -> str:
    """Save a text receipt as fallback."""
    receipt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "receipts")
    os.makedirs(receipt_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"receipt_{name.replace(' ', '_')}_{timestamp}.txt"
    filepath = os.path.join(receipt_dir, filename)

    text = generate_receipt_text(name, phone, amount_paid, total_amount,
                                 payment_date, payment_mode, remaining)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    logger.info(f"Text receipt saved: {filepath}")
    return filepath
