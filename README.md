# Mess Manager — Subscription & Payment Management System

A production-ready mobile application built with **Python + Kivy + SQLite** for managing mess subscriptions, payments, and member tracking.

## Features
- 👤 **Member Management** — Add, edit, soft-delete members
- 💳 **Auto Subscription** — Fee auto-assigned by gender (₹2200 Male / ₹1800 Female)
- 💰 **Payment Tracking** — Record payments with auto status (Paid/Partial/Unpaid)
- 📊 **Dashboard** — Revenue, pending, member stats, and due alerts
- 📅 **Calendar View** — Color-coded monthly payment calendar
- ⏰ **Reminders** — Upcoming, due today, and overdue alerts
- 📈 **Reports** — Monthly revenue, pending payments, member list + CSV export
- 🧾 **Receipts** — PDF receipt generation via ReportLab
- 🔁 **Auto Cycle** — Monthly subscription renewal with pending carry-forward

## Quick Start

```bash
# Install dependencies
pip install kivy reportlab

# Run the app
python main.py
```

## Project Structure
```
mess_management/
├── main.py              # Entry point
├── database/            # SQLite connection & schema
├── services/            # Business logic layer
├── screens/             # UI screens (Dashboard, Members, Payments, etc.)
├── widgets/             # Reusable UI components
└── utils/               # Constants, validators, helpers, logger
```

## Color Coding
- 🟢 **Green** → Paid
- 🟡 **Yellow** → Partial
- 🔴 **Red** → Unpaid / Overdue

## Sample Data
On first run, the app seeds 10 sample members with varied payment records for demo.
