"""Payment list item card widget."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from utils.constants import COLORS
from utils.helpers import format_currency, format_date


class PaymentCard(BoxLayout):
    """Card displaying payment info with color-coded status."""
    def __init__(self, payment_data, on_tap=None, **kwargs):
        super().__init__(
            orientation='horizontal', size_hint_y=None, height=dp(78),
            padding=[dp(12), dp(8)], spacing=dp(10), **kwargs
        )
        self.payment_data = payment_data
        self.on_tap_cb = on_tap

        status = payment_data.get("status", "Unpaid")
        status_colors = {"Paid": "success", "Partial": "warning", "Unpaid": "danger"}
        sc = COLORS[status_colors.get(status, "danger")]

        with self.canvas.before:
            Color(*COLORS["card_bg"])
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(*sc)
            self.side = RoundedRectangle(pos=self.pos, size=(dp(4), self.height), radius=[dp(2)])
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.bind(on_touch_down=self._on_touch)

        # Info section
        info = BoxLayout(orientation='vertical', spacing=dp(2))
        info.add_widget(Label(text=payment_data.get("name", ""), font_size=dp(14), bold=True,
                              color=COLORS["text_primary"], halign='left', valign='bottom',
                              text_size=(dp(160), None)))
        date_txt = format_date(payment_data.get("payment_date", ""))
        mode = payment_data.get("payment_mode", "") or ""
        info.add_widget(Label(text=f"{date_txt}  |  {mode}", font_size=dp(10),
                              color=COLORS["text_secondary"], halign='left', valign='top',
                              text_size=(dp(160), None)))
        self.add_widget(info)

        # Amount section
        amounts = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(100), spacing=dp(2))
        amounts.add_widget(Label(
            text=format_currency(payment_data.get("paid_amount", 0)),
            font_size=dp(15), bold=True, color=COLORS["success"],
            halign='right', valign='bottom', text_size=(dp(95), None)))
        pending = payment_data.get("pending_amount", 0)
        if pending > 0:
            amounts.add_widget(Label(
                text=f"Due: {format_currency(pending)}",
                font_size=dp(10), color=COLORS["danger"],
                halign='right', valign='top', text_size=(dp(95), None)))
        else:
            amounts.add_widget(Label(text="", size_hint_y=0.4))
        self.add_widget(amounts)

        # Status badge
        badge = Label(text=status, font_size=dp(9), bold=True, color=sc,
                      size_hint_x=None, width=dp(52), halign='center', valign='middle')
        self.add_widget(badge)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.side.pos = self.pos
        self.side.size = (dp(4), self.height)

    def _on_touch(self, instance, touch):
        if self.collide_point(*touch.pos) and self.on_tap_cb:
            self.on_tap_cb(self.payment_data)
            return True
