"""Reminders screen — grouped reminder view."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.constants import COLORS
from widgets.reminder_card import ReminderCard
from services.reminder_service import get_all_reminders


class RemindersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="reminders", **kwargs)
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
        header.add_widget(Label(text="Reminders", font_size=dp(20), bold=True,
                                color=COLORS["white"], halign='left', text_size=(dp(200), None)))
        root.add_widget(header)

        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None,
                                  spacing=dp(8), padding=dp(12))
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)

    def refresh(self):
        self.content.clear_widgets()
        reminders = get_all_reminders()

        sections = [
            ("Overdue", reminders["overdue"], "danger"),
            ("Due Today", reminders["due_today"], "warning"),
            ("Upcoming", reminders["upcoming"], "primary_light"),
        ]

        has_any = False
        for title, items, color_key in sections:
            if items:
                has_any = True
                label = Label(text=f"{title} ({len(items)})", font_size=dp(14), bold=True,
                              color=COLORS[color_key], size_hint_y=None, height=dp(30),
                              halign='left', valign='middle')
                label.bind(size=label.setter('text_size'))
                self.content.add_widget(label)
                for r in items:
                    self.content.add_widget(ReminderCard(r, on_tap=self._on_tap))

        if not has_any:
            self.content.add_widget(
                Label(text="All dues are clear!\nNo reminders at this time.",
                      font_size=dp(15), color=COLORS["success"],
                      size_hint_y=None, height=dp(100), halign='center'))

    def _on_tap(self, data):
        if self.manager:
            pay_screen = self.manager.get_screen("payments")
            if hasattr(pay_screen, 'prefill_member'):
                pay_screen.prefill_member(data.get("member_id"))
            self.manager.current = "payments"
