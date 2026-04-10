"""Dashboard stat card widget."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from utils.constants import COLORS


class StatCard(BoxLayout):
    """Rounded stat card with icon, label, and value."""
    def __init__(self, icon="#", title="Stat", value="0", color_key="primary", **kwargs):
        super().__init__(
            orientation='vertical', size_hint=(None, None),
            size=(dp(150), dp(90)), padding=dp(10), spacing=dp(4), **kwargs
        )
        card_color = COLORS.get(color_key, COLORS["primary"])
        with self.canvas.before:
            Color(*card_color, 0.12)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*card_color)
            self.border = RoundedRectangle(pos=self.pos, size=(self.width, dp(3)), radius=[dp(12)])
        self.bind(pos=self._update, size=self._update)

        top = BoxLayout(size_hint_y=0.4, spacing=dp(5))
        top.add_widget(Label(text=icon, font_size=dp(18), size_hint_x=0.3, halign='left', valign='middle'))
        top.add_widget(Label(text=title, font_size=dp(11), color=COLORS["text_secondary"],
                             size_hint_x=0.7, halign='left', valign='middle', text_size=(dp(80), None)))
        self.add_widget(top)

        self.value_label = Label(
            text=str(value), font_size=dp(22), bold=True,
            color=card_color, size_hint_y=0.6, halign='left', valign='middle',
        )
        self.value_label.bind(size=self.value_label.setter('text_size'))
        self.add_widget(self.value_label)

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.pos = (self.pos[0], self.pos[1] + self.height - dp(3))
        self.border.size = (self.width, dp(3))

    def update_value(self, value):
        self.value_label.text = str(value)
