"""Dashboard screen — overview with stats, reminders, and quick actions."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.constants import COLORS
from utils.helpers import format_currency
from widgets.stat_card import StatCard
from widgets.reminder_card import ReminderCard
from services.payment_service import get_revenue_summary
from services.member_service import get_member_count
from services.reminder_service import get_dashboard_reminders


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="dashboard", **kwargs)
        self.stat_cards = {}
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
            self._hdr_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda *a: setattr(self._hdr_bg, 'pos', header.pos),
                    size=lambda *a: setattr(self._hdr_bg, 'size', header.size))
        header.add_widget(Label(text="Dashboard", font_size=dp(20), bold=True,
                                color=COLORS["white"], halign='left', valign='middle',
                                text_size=(dp(250), None)))
        root.add_widget(header)

        # Scrollable content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(12), spacing=dp(12))
        content.bind(minimum_height=content.setter('height'))

        # Stats grid (2x3)
        stats_grid = GridLayout(cols=2, size_hint_y=None, height=dp(300), spacing=dp(10), padding=dp(4))
        card_defs = [
            ("total_revenue", "Rev.", "Total Revenue", "Rs.0", "success"),
            ("total_pending", "Due", "Total Pending", "Rs.0", "danger"),
            ("total_members", "Mem.", "Total Members", "0", "primary"),
            ("male_count", "M", "Male Members", "0", "primary_light"),
            ("female_count", "F", "Female Members", "0", "accent"),
            ("due_count", "!", "Dues Alert", "0", "warning"),
        ]
        for key, icon, title, default, color in card_defs:
            card = StatCard(icon=icon, title=title, value=default, color_key=color)
            card.size_hint = (1, None)
            card.height = dp(90)
            self.stat_cards[key] = card
            stats_grid.add_widget(card)
        content.add_widget(stats_grid)

        # Reminders section
        section_label = Label(text="Upcoming Dues & Reminders", font_size=dp(15), bold=True,
                              color=COLORS["text_primary"], size_hint_y=None, height=dp(30),
                              halign='left', valign='middle')
        section_label.bind(size=section_label.setter('text_size'))
        content.add_widget(section_label)

        self.reminders_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
        self.reminders_container.bind(minimum_height=self.reminders_container.setter('height'))
        content.add_widget(self.reminders_container)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh_data(), 0.1)

    def refresh_data(self):
        # Revenue stats
        rev = get_revenue_summary()
        self.stat_cards["total_revenue"].update_value(format_currency(rev.get("total_revenue", 0)))
        self.stat_cards["total_pending"].update_value(format_currency(rev.get("total_pending", 0)))

        # Member stats
        counts = get_member_count()
        self.stat_cards["total_members"].update_value(str(counts.get("active", 0)))
        self.stat_cards["male_count"].update_value(str(counts.get("male", 0)))
        self.stat_cards["female_count"].update_value(str(counts.get("female", 0)))

        # Reminders
        reminders = get_dashboard_reminders()
        self.stat_cards["due_count"].update_value(str(len(reminders)))

        self.reminders_container.clear_widgets()
        if reminders:
            for r in reminders:
                card = ReminderCard(r, on_tap=self._on_reminder_tap)
                self.reminders_container.add_widget(card)
        else:
            self.reminders_container.add_widget(
                Label(text="✅ No pending dues!", font_size=dp(14),
                      color=COLORS["success"], size_hint_y=None, height=dp(40)))

    def _on_reminder_tap(self, data):
        if self.manager:
            pay_screen = self.manager.get_screen("payments")
            if hasattr(pay_screen, 'prefill_member'):
                pay_screen.prefill_member(data.get("member_id"))
            self.manager.current = "payments"
