"""Reports screen — generate and export reports."""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import date

from utils.constants import COLORS
from utils.helpers import format_currency, get_month_name
from services.report_service import (
    get_monthly_revenue_report, get_pending_payments_report,
    get_member_list_report, export_monthly_revenue_csv,
    export_pending_payments_csv, export_member_list_csv,
)
from services.receipt_service import generate_receipt_pdf


class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="reports", **kwargs)
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
        header.add_widget(Label(text="Reports", font_size=dp(20), bold=True,
                                color=COLORS["white"], halign='left', text_size=(dp(200), None)))
        root.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None,
                             spacing=dp(12), padding=dp(12))
        content.bind(minimum_height=content.setter('height'))

        # Report buttons
        reports = [
            ("Monthly Revenue Report", "View and export monthly revenue data", self._show_revenue_report),
            ("Pending Payments Report", "View all pending and partial payments", self._show_pending_report),
            ("Member List Report", "Complete member directory with status", self._show_member_report),
            ("Export Revenue (CSV)", "Export monthly revenue to CSV file", self._export_revenue),
            ("Export Pending (CSV)", "Export pending payments to CSV", self._export_pending),
            ("Export Members (CSV)", "Export member list to CSV", self._export_members),
        ]

        for title, desc, callback in reports:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(72),
                              padding=dp(12), spacing=dp(4))
            with card.canvas.before:
                Color(*COLORS["card_bg"])
                card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
            card.bind(pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
                      size=lambda *a, c=card: setattr(c._bg, 'size', c.size))

            row = BoxLayout(spacing=dp(10))
            info = BoxLayout(orientation='vertical')
            info.add_widget(Label(text=title, font_size=dp(14), bold=True,
                                  color=COLORS["text_primary"], halign='left',
                                  text_size=(dp(230), None)))
            info.add_widget(Label(text=desc, font_size=dp(10),
                                  color=COLORS["text_secondary"], halign='left',
                                  text_size=(dp(230), None)))
            row.add_widget(info)

            btn = Button(text=">", font_size=dp(18), size_hint_x=None, width=dp(44),
                         background_color=COLORS["primary_light"], color=COLORS["white"])
            btn.bind(on_release=lambda inst, cb=callback: cb())
            row.add_widget(btn)
            card.add_widget(row)
            content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _show_revenue_report(self):
        today = date.today()
        report = get_monthly_revenue_report(today.year, today.month)
        summary = report["summary"]

        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))
        content.add_widget(Label(
            text=f"Revenue: {get_month_name(today.month)} {today.year}",
            font_size=dp(16), bold=True, color=COLORS["primary"],
            size_hint_y=None, height=dp(30)))

        stats = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        stats.add_widget(Label(text=f"Collected\n{format_currency(summary.get('total_collected', 0))}",
                               font_size=dp(12), color=COLORS["success"], halign='center'))
        stats.add_widget(Label(text=f"Pending\n{format_currency(summary.get('total_pending', 0))}",
                               font_size=dp(12), color=COLORS["danger"], halign='center'))
        stats.add_widget(Label(text=f"Members\n{summary.get('member_count', 0)}",
                               font_size=dp(12), color=COLORS["primary"], halign='center'))
        content.add_widget(stats)

        # Data table
        scroll = ScrollView(size_hint_y=1)
        table = GridLayout(cols=4, size_hint_y=None, spacing=dp(2), padding=dp(4))
        table.bind(minimum_height=table.setter('height'))

        for h in ["Name", "Paid", "Pending", "Status"]:
            table.add_widget(Label(text=h, font_size=dp(10), bold=True,
                                   color=COLORS["white"], size_hint_y=None, height=dp(24),
                                   halign='center'))

        for row in report["data"][:20]:
            table.add_widget(Label(text=row.get("name", "")[:15], font_size=dp(10),
                                   color=COLORS["text_primary"], size_hint_y=None, height=dp(22)))
            table.add_widget(Label(text=format_currency(row.get("paid_amount", 0)), font_size=dp(10),
                                   color=COLORS["success"], size_hint_y=None, height=dp(22)))
            table.add_widget(Label(text=format_currency(row.get("pending_amount", 0)), font_size=dp(10),
                                   color=COLORS["danger"], size_hint_y=None, height=dp(22)))
            sc = {"Paid": COLORS["success"], "Partial": COLORS["warning"], "Unpaid": COLORS["danger"]}
            table.add_widget(Label(text=row.get("status", ""), font_size=dp(10),
                                   color=sc.get(row.get("status"), COLORS["text_primary"]),
                                   size_hint_y=None, height=dp(22)))

        scroll.add_widget(table)
        content.add_widget(scroll)

        popup = Popup(title="Monthly Revenue", content=content, size_hint=(0.95, 0.8))
        popup.open()

    def _show_pending_report(self):
        data = get_pending_payments_report()
        content = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(10))
        content.add_widget(Label(text=f"Pending Payments ({len(data)} records)",
                                 font_size=dp(15), bold=True, color=COLORS["danger"],
                                 size_hint_y=None, height=dp(28)))
        scroll = ScrollView()
        table = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        table.bind(minimum_height=table.setter('height'))
        for row in data:
            txt = f"{row['name']} | Due: {format_currency(row['pending_amount'])} | {row['status']}"
            table.add_widget(Label(text=txt, font_size=dp(11), color=COLORS["text_primary"],
                                   size_hint_y=None, height=dp(22), halign='left',
                                   text_size=(dp(300), None)))
        scroll.add_widget(table)
        content.add_widget(scroll)
        popup = Popup(title="Pending Payments", content=content, size_hint=(0.95, 0.7))
        popup.open()

    def _show_member_report(self):
        data = get_member_list_report()
        content = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(10))
        content.add_widget(Label(text=f"All Members ({len(data)})",
                                 font_size=dp(15), bold=True, color=COLORS["primary"],
                                 size_hint_y=None, height=dp(28)))
        scroll = ScrollView()
        table = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        table.bind(minimum_height=table.setter('height'))
        for row in data:
            txt = f"{row['name']} | {row['phone']} | {row['gender']} | {row.get('status', '')}"
            table.add_widget(Label(text=txt, font_size=dp(11), color=COLORS["text_primary"],
                                   size_hint_y=None, height=dp(22), halign='left',
                                   text_size=(dp(300), None)))
        scroll.add_widget(table)
        content.add_widget(scroll)
        popup = Popup(title="Member Directory", content=content, size_hint=(0.95, 0.7))
        popup.open()

    def _export_revenue(self):
        path = export_monthly_revenue_csv()
        self._show_export_result(path)

    def _export_pending(self):
        path = export_pending_payments_csv()
        self._show_export_result(path)

    def _export_members(self):
        path = export_member_list_csv()
        self._show_export_result(path)

    def _show_export_result(self, path):
        if path:
            msg = f"Exported successfully!\n\n{path}"
            color = COLORS["success"]
        else:
            msg = "No data to export or export failed."
            color = COLORS["danger"]
        popup = Popup(title="Export", size_hint=(0.8, 0.3),
                      content=Label(text=msg, font_size=dp(12), color=color, halign='center'))
        popup.open()
