"""Filter bar widget for search and quick filters."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from utils.constants import COLORS


class FilterBar(BoxLayout):
    """Reusable filter toolbar with search and dropdown filters."""
    def __init__(self, on_search=None, on_filter=None, filters=None, quick_filters=None, **kwargs):
        super().__init__(
            orientation='vertical', size_hint_y=None, height=dp(100),
            padding=dp(8), spacing=dp(6), **kwargs
        )
        self.on_search_cb = on_search
        self.on_filter_cb = on_filter

        with self.canvas.before:
            Color(*COLORS["card_bg"])
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update, size=self._update)

        # Search row
        search_row = BoxLayout(size_hint_y=0.5, spacing=dp(6))
        self.search_input = TextInput(
            hint_text="🔍 Search by name or phone...",
            multiline=False, size_hint_x=0.7, font_size=dp(13),
            background_color=(0.96, 0.96, 0.96, 1), foreground_color=COLORS["text_primary"],
            padding=[dp(10), dp(8)],
        )
        self.search_input.bind(text=self._on_search)
        search_row.add_widget(self.search_input)

        if filters:
            for name, values in filters.items():
                spinner = Spinner(
                    text=name, values=["All"] + values,
                    size_hint_x=0.3, font_size=dp(11),
                    background_color=COLORS["primary_light"],
                    color=COLORS["white"],
                )
                spinner.filter_name = name
                spinner.bind(text=self._on_filter_change)
                search_row.add_widget(spinner)

        self.add_widget(search_row)

        # Quick filter chips
        if quick_filters:
            chip_row = BoxLayout(size_hint_y=0.5, spacing=dp(4))
            for label, key in quick_filters:
                chip = Button(
                    text=label, font_size=dp(10),
                    background_color=COLORS["primary"], color=COLORS["white"],
                    size_hint_x=None, width=dp(90),
                )
                chip.filter_key = key
                chip.bind(on_release=self._on_quick_filter)
                chip_row.add_widget(chip)
            chip_row.add_widget(BoxLayout())  # spacer
            self.add_widget(chip_row)

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _on_search(self, instance, text):
        if self.on_search_cb:
            self.on_search_cb(text)

    def _on_filter_change(self, spinner, text):
        if self.on_filter_cb:
            value = None if text == "All" else text
            self.on_filter_cb(spinner.filter_name, value)

    def _on_quick_filter(self, btn):
        if self.on_filter_cb:
            self.on_filter_cb("quick", btn.filter_key)
