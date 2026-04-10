"""More screen — hub for Reports, Reminders, Receipts."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from utils.constants import COLORS


class MoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="more", **kwargs)
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
        header.add_widget(Label(text="More", font_size=dp(20), bold=True,
                                color=COLORS["white"], halign='left', text_size=(dp(200), None)))
        root.add_widget(header)

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(16))

        menu_items = [
            ("(!)", "Reminders", "View due alerts & notifications", "reminders"),
            ("(+)", "Reports", "Revenue & pending reports, CSV export", "reports"),
            ("(=)", "Generate Receipt", "Create payment receipts (PDF)", "receipt_action"),
        ]

        for icon, title, desc, action in menu_items:
            card = BoxLayout(size_hint_y=None, height=dp(68), padding=dp(12), spacing=dp(12))
            with card.canvas.before:
                Color(*COLORS["card_bg"])
                card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
            card.bind(pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
                      size=lambda *a, c=card: setattr(c._bg, 'size', c.size))

            card.add_widget(Label(text=icon, font_size=dp(24), size_hint_x=None, width=dp(40)))
            info = BoxLayout(orientation='vertical')
            info.add_widget(Label(text=title, font_size=dp(15), bold=True,
                                  color=COLORS["text_primary"], halign='left',
                                  text_size=(dp(200), None)))
            info.add_widget(Label(text=desc, font_size=dp(11),
                                  color=COLORS["text_secondary"], halign='left',
                                  text_size=(dp(200), None)))
            card.add_widget(info)

            btn = Button(text=">", font_size=dp(18), size_hint_x=None, width=dp(40),
                         background_color=COLORS["primary_light"], color=COLORS["white"])
            btn.bind(on_release=lambda inst, a=action: self._navigate(a))
            card.add_widget(btn)
            content.add_widget(card)

        # App info
        content.add_widget(BoxLayout())  # spacer
        content.add_widget(Label(
            text="Mess Manager v1.0.0\nSubscription & Payment Management",
            font_size=dp(11), color=COLORS["text_secondary"],
            size_hint_y=None, height=dp(40), halign='center'))

        root.add_widget(content)
        self.add_widget(root)

    def _navigate(self, action):
        if action == "receipt_action":
            self._generate_receipt()
        elif self.manager and action in self.manager.screen_names:
            self.manager.current = action

    def _generate_receipt(self):
        from kivy.uix.popup import Popup
        from kivy.uix.spinner import Spinner
        from services.member_service import get_active_members
        from services.payment_service import get_payment_info
        from services.receipt_service import generate_receipt_pdf
        from utils.helpers import format_currency

        members = get_active_members()
        if not members:
            Popup(title="No Data", size_hint=(0.7, 0.3),
                  content=Label(text="No active members", font_size=dp(14))).open()
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(16))
        member_names = [f"{m['name']} ({m['phone']})" for m in members]
        spinner = Spinner(text="Select Member", values=member_names,
                          size_hint_y=None, height=dp(40),
                          background_color=COLORS["primary_light"], color=COLORS["white"])
        content.add_widget(spinner)

        result_label = Label(text="", font_size=dp(12), color=COLORS["text_primary"],
                             size_hint_y=None, height=dp(60), halign='center')
        content.add_widget(result_label)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = Button(text="Cancel", background_color=COLORS["text_secondary"])
        gen_btn = Button(text="Generate PDF", background_color=COLORS["success"],
                         color=COLORS["white"], bold=True)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(gen_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Generate Receipt", content=content, size_hint=(0.9, 0.5))
        cancel_btn.bind(on_release=popup.dismiss)

        def on_generate(*args):
            idx = member_names.index(spinner.text) if spinner.text in member_names else -1
            if idx < 0:
                result_label.text = "Please select a member"
                return
            m = members[idx]
            info = get_payment_info(m["member_id"])
            if not info:
                result_label.text = "No payment data found"
                return
            path = generate_receipt_pdf(
                info.get("name", m["name"]), info.get("phone", m["phone"]),
                info.get("paid_amount", 0), info.get("total_amount", 0),
                info.get("payment_date", ""), info.get("payment_mode", ""),
                info.get("pending_amount", 0),
            )
            if path:
                result_label.text = f"Receipt saved!\n{path}"
                result_label.color = COLORS["success"]
            else:
                result_label.text = "Failed to generate receipt"
                result_label.color = COLORS["danger"]

        gen_btn.bind(on_release=on_generate)
        popup.open()
