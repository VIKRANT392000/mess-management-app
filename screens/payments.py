"""Payments screen — record payments, view history, filters."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.constants import COLORS, PAYMENT_MODES, PAYMENT_STATUSES, GENDERS
from utils.helpers import format_currency, today_str, calc_payment_status
from widgets.payment_card import PaymentCard
from widgets.filter_bar import FilterBar
from services.payment_service import (
    get_all_payments, record_payment, get_payment_info,
    get_due_today, get_overdue, get_paid_this_month,
)
from services.member_service import get_active_members
from services.subscription_service import get_active_subscription


class PaymentsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="payments", **kwargs)
        self.current_filters = {}
        self._prefill_member_id = None
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical')
        with root.canvas.before:
            Color(*COLORS["bg"])
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, 'pos', root.pos),
                  size=lambda *a: setattr(self._bg, 'size', root.size))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(16), dp(8)])
        with header.canvas.before:
            Color(*COLORS["primary"])
            self._hdr = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda *a: setattr(self._hdr, 'pos', header.pos),
                    size=lambda *a: setattr(self._hdr, 'size', header.size))
        header.add_widget(Label(text="Payments", font_size=dp(20), bold=True,
                                color=COLORS["white"], halign='left', text_size=(dp(200), None)))
        pay_btn = Button(text="+ Pay", size_hint=(None, None), size=(dp(70), dp(36)),
                         font_size=dp(13), background_color=COLORS["success"],
                         color=COLORS["white"], bold=True)
        pay_btn.bind(on_release=lambda *a: self._show_payment_form())
        header.add_widget(pay_btn)
        root.add_widget(header)

        # Filter
        self.filter_bar = FilterBar(
            on_search=self._on_search, on_filter=self._on_filter,
            filters={"Status": PAYMENT_STATUSES, "Gender": GENDERS},
            quick_filters=[("Due Today", "due_today"), ("Overdue", "overdue"), ("Paid Month", "paid_month")],
        )
        root.add_widget(self.filter_bar)

        # Payment list
        scroll = ScrollView()
        self.list_container = BoxLayout(orientation='vertical', size_hint_y=None,
                                        spacing=dp(6), padding=[dp(8), dp(4)])
        self.list_container.bind(minimum_height=self.list_container.setter('height'))
        scroll.add_widget(self.list_container)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self._check_prefill(), 0.1)

    def _check_prefill(self):
        if self._prefill_member_id:
            mid = self._prefill_member_id
            self._prefill_member_id = None
            self._show_payment_form(mid)
        else:
            self.refresh_list()

    def prefill_member(self, member_id):
        self._prefill_member_id = member_id

    def refresh_list(self, data=None):
        self.list_container.clear_widgets()
        if data is None:
            data = get_all_payments(
                status_filter=self.current_filters.get("status"),
                gender_filter=self.current_filters.get("gender"),
                search=self.current_filters.get("search"),
            )
        if not data:
            self.list_container.add_widget(
                Label(text="No payment records found.", font_size=dp(14),
                      color=COLORS["text_secondary"], size_hint_y=None, height=dp(60)))
            return
        for p in data:
            self.list_container.add_widget(PaymentCard(p, on_tap=self._on_payment_tap))

    def _on_search(self, text):
        self.current_filters["search"] = text if text.strip() else None
        self.refresh_list()

    def _on_filter(self, name, value):
        if name == "quick":
            if value == "due_today":
                self.refresh_list(get_due_today())
            elif value == "overdue":
                self.refresh_list(get_overdue())
            elif value == "paid_month":
                self.refresh_list(get_paid_this_month())
        else:
            if name == "Status":
                self.current_filters["status"] = value
            elif name == "Gender":
                self.current_filters["gender"] = value
            self.refresh_list()

    def _show_payment_form(self, prefill_id=None):
        members = get_active_members()
        if not members:
            popup = Popup(title="No Members", size_hint=(0.7, 0.3),
                          content=Label(text="Add members first!", font_size=dp(14)))
            popup.open()
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(16))

        # Member selector
        content.add_widget(Label(text="Select Member", font_size=dp(12),
                                 color=COLORS["text_secondary"], size_hint_y=None, height=dp(18),
                                 halign='left', text_size=(dp(280), None)))
        member_names = [f"{m['name']} ({m['phone']})" for m in members]
        member_spinner = Spinner(text="Select Member", values=member_names,
                                 size_hint_y=None, height=dp(40), font_size=dp(13),
                                 background_color=COLORS["primary_light"], color=COLORS["white"])
        content.add_widget(member_spinner)

        # Info labels
        info_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50), spacing=dp(4))
        total_label = Label(text="Total: ₹0.00", font_size=dp(13), color=COLORS["text_primary"],
                            halign='left', text_size=(dp(280), None), size_hint_y=None, height=dp(22))
        pending_label = Label(text="Pending: ₹0.00", font_size=dp(13), color=COLORS["danger"],
                              halign='left', text_size=(dp(280), None), size_hint_y=None, height=dp(22))
        info_box.add_widget(total_label)
        info_box.add_widget(pending_label)
        content.add_widget(info_box)

        selected_member = {"id": None, "total": 0, "already_paid": 0, "remaining": 0}

        def on_member_select(spinner, text):
            idx = member_names.index(text) if text in member_names else -1
            if idx < 0:
                return
            m = members[idx]
            selected_member["id"] = m["member_id"]
            sub = get_active_subscription(m["member_id"])
            if sub:
                info = get_payment_info(m["member_id"])
                total = info["total_amount"] if info else sub["fee"]
                paid = info["paid_amount"] if info else 0
                remaining = total - paid
                selected_member.update({"total": total, "already_paid": paid, "remaining": remaining})
                total_label.text = f"Total: {format_currency(total)}  |  Already Paid: {format_currency(paid)}"
                pending_label.text = f"Remaining to Pay: {format_currency(remaining)}"
            else:
                total_label.text = "No active subscription"
                pending_label.text = ""

        member_spinner.bind(text=on_member_select)

        # Prefill
        if prefill_id:
            for i, m in enumerate(members):
                if m["member_id"] == prefill_id:
                    member_spinner.text = member_names[i]
                    break

        # Paid amount
        content.add_widget(Label(text="Amount to Pay", font_size=dp(12),
                                 color=COLORS["text_secondary"], size_hint_y=None, height=dp(18),
                                 halign='left', text_size=(dp(280), None)))
        paid_input = TextInput(hint_text="Enter amount", multiline=False,
                               size_hint_y=None, height=dp(40), font_size=dp(14), input_filter='float')
        content.add_widget(paid_input)

        # Real-time calculation
        calc_label = Label(text="", font_size=dp(12), color=COLORS["primary"],
                           size_hint_y=None, height=dp(20), halign='left', text_size=(dp(280), None))
        content.add_widget(calc_label)

        def on_amount_change(instance, text):
            try:
                amt = float(text) if text else 0
                new_pending = selected_member["remaining"] - amt
                status = calc_payment_status(selected_member["total"], selected_member["already_paid"] + amt)
                color = COLORS["success"] if status == "Paid" else COLORS["warning"] if status == "Partial" else COLORS["danger"]
                calc_label.color = color
                calc_label.text = f"After payment → Pending: {format_currency(max(0, new_pending))} | Status: {status}"
            except ValueError:
                calc_label.text = ""

        paid_input.bind(text=on_amount_change)

        # Payment mode
        content.add_widget(Label(text="Payment Mode", font_size=dp(12),
                                 color=COLORS["text_secondary"], size_hint_y=None, height=dp(18),
                                 halign='left', text_size=(dp(280), None)))
        mode_spinner = Spinner(text="Select Mode", values=PAYMENT_MODES,
                               size_hint_y=None, height=dp(40), font_size=dp(13),
                               background_color=COLORS["primary_light"], color=COLORS["white"])
        content.add_widget(mode_spinner)

        # Error
        error_label = Label(text="", font_size=dp(11), color=COLORS["danger"],
                            size_hint_y=None, height=dp(18), halign='left', text_size=(dp(280), None))
        content.add_widget(error_label)

        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = Button(text="Cancel", font_size=dp(14), background_color=COLORS["text_secondary"])
        save_btn = Button(text="Record Payment", font_size=dp(14),
                          background_color=COLORS["success"], color=COLORS["white"], bold=True)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Record Payment", content=content, size_hint=(0.95, 0.85),
                      title_color=COLORS["primary"], separator_color=COLORS["primary"])
        cancel_btn.bind(on_release=popup.dismiss)

        def on_save(*args):
            if not selected_member["id"]:
                error_label.text = "Please select a member"
                return
            if mode_spinner.text == "Select Mode":
                error_label.text = "Please select payment mode"
                return
            result = record_payment(selected_member["id"], paid_input.text, mode_spinner.text)
            if result["success"]:
                popup.dismiss()
                self.refresh_list()
            else:
                error_label.text = " | ".join(result.get("errors", {}).values())

        save_btn.bind(on_release=on_save)
        popup.open()

    def _on_payment_tap(self, data):
        """Show payment detail or generate receipt."""
        from services.receipt_service import generate_receipt_text
        text = generate_receipt_text(
            data.get("name", ""), data.get("phone", ""),
            data.get("paid_amount", 0), data.get("total_amount", 0),
            data.get("payment_date", ""), data.get("payment_mode", ""),
            data.get("pending_amount", 0),
        )
        content = BoxLayout(orientation='vertical', padding=dp(8))
        content.add_widget(Label(text=text, font_size=dp(10), font_name="RobotoMono",
                                 color=COLORS["text_primary"], halign='left', valign='top',
                                 text_size=(dp(320), None), size_hint_y=None, height=dp(350)))
        popup = Popup(title="Payment Receipt", content=content, size_hint=(0.95, 0.7))
        popup.open()
