"""Calendar cell widget."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from utils.constants import COLORS


class CalendarCell(BoxLayout):
    """Single day cell for the calendar view."""
    def __init__(self, day=0, status=None, count=0, **kwargs):
        super().__init__(
            orientation='vertical', size_hint=(1, 1),
            padding=dp(2), **kwargs
        )
        color_map = {
            "Paid": COLORS["success"],
            "Partial": COLORS["warning"],
            "Unpaid": COLORS["danger"],
            None: COLORS["bg"],
        }
        bg_color = color_map.get(status, COLORS["bg"])

        with self.canvas.before:
            Color(*bg_color, 0.25 if status else 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(6)])
        self.bind(pos=self._update, size=self._update)

        text_color = COLORS["text_primary"] if day > 0 else COLORS["transparent"]
        self.add_widget(Label(
            text=str(day) if day > 0 else "",
            font_size=dp(12), color=text_color,
            bold=status is not None, halign='center', valign='middle',
        ))
        if count > 0 and status:
            self.add_widget(Label(
                text=f"{count}", font_size=dp(8),
                color=color_map.get(status, COLORS["text_secondary"]),
                halign='center', valign='top',
            ))

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
