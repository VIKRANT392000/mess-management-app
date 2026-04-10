"""Calendar view screen — monthly calendar with color-coded payment status."""
from datetime import date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.constants import COLORS
from utils.helpers import get_month_name, get_days_in_month, get_first_weekday
from widgets.calendar_cell import CalendarCell
from services.payment_service import get_calendar_data


class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="calendar", **kwargs)
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
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
        header.add_widget(Label(text="Calendar", font_size=dp(20), bold=True,
                                color=COLORS["white"], halign='left', text_size=(dp(200), None)))
        root.add_widget(header)

        # Month navigation
        nav = BoxLayout(size_hint_y=None, height=dp(44), padding=dp(8), spacing=dp(4))
        prev_btn = Button(text="<", size_hint_x=None, width=dp(44), font_size=dp(18),
                          background_color=COLORS["primary_light"], color=COLORS["white"])
        prev_btn.bind(on_release=self._prev_month)
        nav.add_widget(prev_btn)

        self.month_label = Label(text="", font_size=dp(16), bold=True,
                                 color=COLORS["text_primary"], halign='center')
        nav.add_widget(self.month_label)

        next_btn = Button(text=">", size_hint_x=None, width=dp(44), font_size=dp(18),
                          background_color=COLORS["primary_light"], color=COLORS["white"])
        next_btn.bind(on_release=self._next_month)
        nav.add_widget(next_btn)
        root.add_widget(nav)

        # Day headers
        day_headers = GridLayout(cols=7, size_hint_y=None, height=dp(28), padding=[dp(4), 0])
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            day_headers.add_widget(Label(text=day, font_size=dp(11), bold=True,
                                         color=COLORS["text_secondary"], halign='center'))
        root.add_widget(day_headers)

        # Calendar grid
        self.calendar_grid = GridLayout(cols=7, spacing=dp(3), padding=dp(4))
        root.add_widget(self.calendar_grid)

        # Legend
        legend = BoxLayout(size_hint_y=None, height=dp(36), padding=dp(8), spacing=dp(12))
        for label, color_key in [("Paid", "success"), ("Partial", "warning"), ("Pending", "danger")]:
            item = BoxLayout(spacing=dp(4))
            dot = Label(text="*", font_size=dp(14), color=COLORS[color_key],
                        size_hint_x=None, width=dp(18))
            item.add_widget(dot)
            item.add_widget(Label(text=label, font_size=dp(11), color=COLORS["text_secondary"]))
            legend.add_widget(item)
        root.add_widget(legend)

        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh_calendar(), 0.1)

    def refresh_calendar(self):
        self.month_label.text = f"{get_month_name(self.current_month)} {self.current_year}"
        self.calendar_grid.clear_widgets()

        days_in_month = get_days_in_month(self.current_year, self.current_month)
        first_weekday = get_first_weekday(self.current_year, self.current_month)

        # Get payment data for this month
        cal_data = get_calendar_data(self.current_year, self.current_month)
        day_status = {}
        for entry in cal_data:
            day = entry["day"]
            if day not in day_status:
                day_status[day] = {"status": entry["status"], "count": entry["count"]}
            elif entry["status"] == "Unpaid":
                day_status[day] = {"status": "Unpaid", "count": entry["count"]}

        # Blank cells for days before month start
        for _ in range(first_weekday):
            self.calendar_grid.add_widget(CalendarCell(day=0))

        # Day cells
        for day in range(1, days_in_month + 1):
            info = day_status.get(day, {})
            cell = CalendarCell(day=day, status=info.get("status"), count=info.get("count", 0))
            self.calendar_grid.add_widget(cell)

        # Fill remaining cells
        total_cells = first_weekday + days_in_month
        remaining = (7 - total_cells % 7) % 7
        for _ in range(remaining):
            self.calendar_grid.add_widget(CalendarCell(day=0))

    def _prev_month(self, *args):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_calendar()

    def _next_month(self, *args):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_calendar()
