"""Member list item card widget."""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from utils.constants import COLORS


class MemberCard(BoxLayout):
    """Card displaying member info with edit/delete actions."""
    def __init__(self, member_data, on_edit=None, on_delete=None, **kwargs):
        super().__init__(
            orientation='horizontal', size_hint_y=None, height=dp(72),
            padding=[dp(12), dp(8)], spacing=dp(10), **kwargs
        )
        self.member_data = member_data
        self.on_edit_cb = on_edit
        self.on_delete_cb = on_delete

        with self.canvas.before:
            Color(*COLORS["card_bg"])
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Avatar circle
        gender_color = COLORS["primary"] if member_data.get("gender") == "Male" else COLORS["accent"]
        avatar = Label(
            text=member_data.get("name", "?")[0].upper(),
            font_size=dp(18), bold=True, color=COLORS["white"],
            size_hint=(None, None), size=(dp(44), dp(44)),
        )
        with avatar.canvas.before:
            Color(*gender_color)
            avatar._bg = RoundedRectangle(pos=avatar.pos, size=avatar.size, radius=[dp(22)])
        avatar.bind(pos=lambda *a: setattr(avatar._bg, 'pos', avatar.pos),
                     size=lambda *a: setattr(avatar._bg, 'size', avatar.size))
        self.add_widget(avatar)

        # Info
        info = BoxLayout(orientation='vertical', spacing=dp(2))
        info.add_widget(Label(text=member_data.get("name", ""), font_size=dp(14), bold=True,
                              color=COLORS["text_primary"], halign='left', valign='bottom',
                              text_size=(dp(180), None)))
        sub_text = f"{member_data.get('phone', '')}  |  {member_data.get('gender', '')}"
        info.add_widget(Label(text=sub_text, font_size=dp(11),
                              color=COLORS["text_secondary"], halign='left', valign='top',
                              text_size=(dp(180), None)))
        self.add_widget(info)

        # Status badge
        status = member_data.get("status", "Active")
        status_color = COLORS["success"] if status == "Active" else COLORS["text_secondary"]
        badge = Label(text=f"* {status}", font_size=dp(10), color=status_color,
                      size_hint_x=None, width=dp(60), halign='center', valign='middle')
        self.add_widget(badge)

        # Action buttons
        actions = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(36), spacing=dp(4))
        edit_btn = Button(text="Edit", font_size=dp(10), size_hint_y=0.5,
                          background_color=(0, 0, 0, 0), color=COLORS["primary_light"])
        edit_btn.bind(on_release=self._on_edit)
        del_btn = Button(text="X", font_size=dp(12), size_hint_y=0.5, bold=True,
                         background_color=(0, 0, 0, 0), color=COLORS["danger"])
        del_btn.bind(on_release=self._on_delete)
        actions.add_widget(edit_btn)
        actions.add_widget(del_btn)
        self.add_widget(actions)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _on_edit(self, *args):
        if self.on_edit_cb:
            self.on_edit_cb(self.member_data)

    def _on_delete(self, *args):
        if self.on_delete_cb:
            self.on_delete_cb(self.member_data)
