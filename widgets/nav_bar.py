"""Bottom navigation bar widget."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from utils.constants import COLORS


class NavButton(BoxLayout):
    """Single navigation button with icon text and label."""
    def __init__(self, icon_text, label_text, screen_name, nav_bar, **kwargs):
        super().__init__(orientation='vertical', size_hint=(1, 1), **kwargs)
        self.screen_name = screen_name
        self.nav_bar = nav_bar
        self.is_active = False

        self.icon_label = Label(
            text=icon_text, font_size=dp(20), size_hint_y=0.6,
            color=COLORS["text_secondary"], halign='center', valign='middle',
        )
        self.text_label = Label(
            text=label_text, font_size=dp(10), size_hint_y=0.4,
            color=COLORS["text_secondary"], halign='center', valign='middle',
        )
        self.add_widget(self.icon_label)
        self.add_widget(self.text_label)
        self.bind(on_touch_down=self.on_press)

    def on_press(self, instance, touch):
        if self.collide_point(*touch.pos):
            self.nav_bar.set_active(self.screen_name)
            return True

    def set_active(self, active):
        self.is_active = active
        color = COLORS["accent"] if active else COLORS["text_secondary"]
        self.icon_label.color = color
        self.text_label.color = color


class BottomNavBar(BoxLayout):
    """Bottom navigation bar with 5 tabs."""
    def __init__(self, screen_manager=None, **kwargs):
        super().__init__(
            orientation='horizontal', size_hint_y=None, height=dp(60),
            padding=[dp(5), dp(5)], spacing=dp(2), **kwargs
        )
        self.screen_manager = screen_manager
        self.buttons = {}

        with self.canvas.before:
            Color(*COLORS["primary"])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        tabs = [
            ("#", "Home", "dashboard"),
            ("@", "Members", "members"),
            ("$", "Payments", "payments"),
            ("*", "Calendar", "calendar"),
            ("+", "More", "more"),
        ]
        for icon, label, screen in tabs:
            btn = NavButton(icon, label, screen, self)
            self.buttons[screen] = btn
            self.add_widget(btn)

        self.set_active("dashboard")

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def set_active(self, screen_name):
        for name, btn in self.buttons.items():
            btn.set_active(name == screen_name)
        if self.screen_manager and screen_name in self.screen_manager.screen_names:
            self.screen_manager.current = screen_name
