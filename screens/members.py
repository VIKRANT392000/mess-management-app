"""Members screen — list, search, add, edit, delete members."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from utils.constants import COLORS, GENDERS
from utils.helpers import format_date, today_str
from widgets.member_card import MemberCard
from widgets.filter_bar import FilterBar
from services.member_service import (
    get_all_members, add_member, edit_member, delete_member
)
from services.subscription_service import create_subscription


class MembersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="members", **kwargs)
        self.current_filters = {"status": None, "gender": None, "search": None}
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
        header.add_widget(Label(text="Members", font_size=dp(20), bold=True,
                                color=COLORS["white"], halign='left', text_size=(dp(200), None)))
        add_btn = Button(text="+ Add", size_hint=(None, None), size=(dp(70), dp(36)),
                         font_size=dp(13), background_color=COLORS["accent"],
                         color=COLORS["text_primary"], bold=True)
        add_btn.bind(on_release=lambda *a: self._show_member_form())
        header.add_widget(add_btn)
        root.add_widget(header)

        # Filter bar
        self.filter_bar = FilterBar(
            on_search=self._on_search,
            on_filter=self._on_filter,
            filters={"Gender": GENDERS, "Status": ["Active", "Inactive"]},
        )
        root.add_widget(self.filter_bar)

        # Member list
        scroll = ScrollView()
        self.list_container = BoxLayout(orientation='vertical', size_hint_y=None,
                                        spacing=dp(6), padding=[dp(8), dp(4)])
        self.list_container.bind(minimum_height=self.list_container.setter('height'))
        scroll.add_widget(self.list_container)
        root.add_widget(scroll)

        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.1)

    def refresh_list(self):
        self.list_container.clear_widgets()
        members = get_all_members(
            status_filter=self.current_filters.get("status"),
            gender_filter=self.current_filters.get("gender"),
            search=self.current_filters.get("search"),
        )
        if not members:
            self.list_container.add_widget(
                Label(text="No members found.\nTap '+ Add' to add your first member.",
                      font_size=dp(14), color=COLORS["text_secondary"],
                      size_hint_y=None, height=dp(80), halign='center'))
            return
        for m in members:
            card = MemberCard(m, on_edit=self._on_edit, on_delete=self._on_delete)
            self.list_container.add_widget(card)

    def _on_search(self, text):
        self.current_filters["search"] = text if text.strip() else None
        self.refresh_list()

    def _on_filter(self, filter_name, value):
        if filter_name == "Gender":
            self.current_filters["gender"] = value
        elif filter_name == "Status":
            self.current_filters["status"] = value
        self.refresh_list()

    def _show_member_form(self, member_data=None):
        """Show add/edit member popup."""
        is_edit = member_data is not None
        title = "Edit Member" if is_edit else "Add New Member"

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))

        # Name
        content.add_widget(Label(text="Name", font_size=dp(12), color=COLORS["text_secondary"],
                                 size_hint_y=None, height=dp(20), halign='left', text_size=(dp(250), None)))
        name_input = TextInput(text=member_data.get("name", "") if is_edit else "",
                               hint_text="Enter full name", multiline=False,
                               size_hint_y=None, height=dp(40), font_size=dp(14))
        content.add_widget(name_input)

        # Phone
        content.add_widget(Label(text="Phone", font_size=dp(12), color=COLORS["text_secondary"],
                                 size_hint_y=None, height=dp(20), halign='left', text_size=(dp(250), None)))
        phone_input = TextInput(text=member_data.get("phone", "") if is_edit else "",
                                hint_text="10-digit phone number", multiline=False,
                                size_hint_y=None, height=dp(40), font_size=dp(14), input_filter='int')
        content.add_widget(phone_input)

        # Gender
        content.add_widget(Label(text="Gender", font_size=dp(12), color=COLORS["text_secondary"],
                                 size_hint_y=None, height=dp(20), halign='left', text_size=(dp(250), None)))
        gender_spinner = Spinner(text=member_data.get("gender", "Select Gender") if is_edit else "Select Gender",
                                 values=GENDERS, size_hint_y=None, height=dp(40), font_size=dp(14),
                                 background_color=COLORS["primary_light"], color=COLORS["white"])
        content.add_widget(gender_spinner)

        # Joining Date
        content.add_widget(Label(text="Joining Date (YYYY-MM-DD)", font_size=dp(12),
                                 color=COLORS["text_secondary"], size_hint_y=None, height=dp(20),
                                 halign='left', text_size=(dp(250), None)))
        date_input = TextInput(text=member_data.get("joining_date", today_str()) if is_edit else today_str(),
                               hint_text="YYYY-MM-DD", multiline=False,
                               size_hint_y=None, height=dp(40), font_size=dp(14))
        content.add_widget(date_input)

        # Error label
        error_label = Label(text="", font_size=dp(11), color=COLORS["danger"],
                            size_hint_y=None, height=dp(20), halign='left', text_size=(dp(280), None))
        content.add_widget(error_label)

        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = Button(text="Cancel", font_size=dp(14), background_color=COLORS["text_secondary"])
        save_btn = Button(text="Save", font_size=dp(14), background_color=COLORS["success"],
                          color=COLORS["white"], bold=True)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)

        popup = Popup(title=title, content=content, size_hint=(0.9, 0.75),
                      title_color=COLORS["primary"], separator_color=COLORS["primary"])

        cancel_btn.bind(on_release=popup.dismiss)

        def on_save(*args):
            name = name_input.text.strip()
            phone = phone_input.text.strip()
            gender = gender_spinner.text
            joining = date_input.text.strip()

            if gender == "Select Gender":
                error_label.text = "Please select a gender"
                return

            if is_edit:
                result = edit_member(member_data["member_id"], name, phone, gender, joining)
            else:
                result = add_member(name, phone, gender, joining)

            if result["success"]:
                if not is_edit:
                    create_subscription(result["member_id"], gender, joining)
                popup.dismiss()
                self.refresh_list()
            else:
                errors = result.get("errors", {})
                error_label.text = " | ".join(errors.values())

        save_btn.bind(on_release=on_save)
        popup.open()

    def _on_edit(self, member_data):
        self._show_member_form(member_data)

    def _on_delete(self, member_data):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(16))
        content.add_widget(Label(
            text=f"Deactivate {member_data['name']}?\n\nThis will set the member as inactive.\nData will be preserved.",
            font_size=dp(13), color=COLORS["text_primary"], halign='center'))

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = Button(text="Cancel", background_color=COLORS["text_secondary"])
        confirm_btn = Button(text="Deactivate", background_color=COLORS["danger"], color=COLORS["white"])
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Confirm Deactivation", content=content,
                      size_hint=(0.8, 0.4), title_color=COLORS["danger"])
        cancel_btn.bind(on_release=popup.dismiss)

        def confirm(*args):
            delete_member(member_data["member_id"])
            popup.dismiss()
            self.refresh_list()

        confirm_btn.bind(on_release=confirm)
        popup.open()
