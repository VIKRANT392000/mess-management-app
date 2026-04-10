"""Reminder card widget."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from utils.constants import COLORS
from utils.helpers import format_currency, format_date, days_until_due


class ReminderCard(BoxLayout):
    """Card displaying reminder with urgency indicator."""
    def __init__(self, reminder_data, on_tap=None, **kwargs):
        super().__init__(
            orientation='horizontal', size_hint_y=None, height=dp(68),
            padding=[dp(12), dp(8)], spacing=dp(10), **kwargs
        )
        self.data = reminder_data
        self.on_tap_cb = on_tap

        r_type = reminder_data.get("reminder_type", "Normal")
        type_colors = {"Overdue": "danger", "Due Today": "warning", "Upcoming": "primary_light", "Normal": "text_secondary"}
        tc = COLORS[type_colors.get(r_type, "text_secondary")]

        with self.canvas.before:
            Color(*COLORS["card_bg"])
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(*tc)
            self.side = RoundedRectangle(pos=self.pos, size=(dp(4), self.height), radius=[dp(2)])
        self.bind(pos=self._update, size=self._update)
        self.bind(on_touch_down=self._on_touch)

        # Icon
        icons = {"Overdue": "!", "Due Today": "i", "Upcoming": "o"}
        self.add_widget(Label(text=icons.get(r_type, "-"), font_size=dp(16), bold=True,
                              size_hint_x=None, width=dp(30), color=tc))

        # Info
        info = BoxLayout(orientation='vertical', spacing=dp(2))
        info.add_widget(Label(text=reminder_data.get("member_name", ""), font_size=dp(13),
                              bold=True, color=COLORS["text_primary"], halign='left',
                              valign='bottom', text_size=(dp(140), None)))
        due = reminder_data.get("due_date", "")
        days = days_until_due(due)
        if days < 0:
            sub = f"Overdue by {abs(days)} day(s)"
        elif days == 0:
            sub = "Due Today"
        else:
            sub = f"Due in {days} day(s)"
        info.add_widget(Label(text=sub, font_size=dp(10), color=tc,
                              halign='left', valign='top', text_size=(dp(140), None)))
        self.add_widget(info)

        # Amount
        pending = reminder_data.get("pending_amount", 0)
        self.add_widget(Label(text=format_currency(pending), font_size=dp(13),
                              bold=True, color=COLORS["danger"], size_hint_x=None,
                              width=dp(80), halign='right', valign='middle'))

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.side.pos = self.pos
        self.side.size = (dp(4), self.height)

    def _on_touch(self, instance, touch):
        if self.collide_point(*touch.pos) and self.on_tap_cb:
            self.on_tap_cb(self.data)
            return True
