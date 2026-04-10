"""
Mess Manager — Subscription & Payment Management System
Entry point: python main.py
"""

import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', True)
Config.set('kivy', 'window_icon', '')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.metrics import dp

from utils.constants import COLORS, APP_NAME
from utils.logger import logger
from database.models import create_tables, seed_sample_data
from services.subscription_service import auto_cycle_subscriptions

from screens.dashboard import DashboardScreen
from screens.members import MembersScreen
from screens.payments import PaymentsScreen
from screens.calendar_view import CalendarScreen
from screens.reminders import RemindersScreen
from screens.reports import ReportsScreen
from screens.more import MoreScreen
from widgets.nav_bar import BottomNavBar


class MessManagerApp(App):
    def build(self):
        self.title = APP_NAME
        Window.clearcolor = COLORS["bg"]

        # Initialize database
        logger.info("=" * 50)
        logger.info(f"Starting {APP_NAME}")
        logger.info("=" * 50)

        try:
            create_tables()
            seed_sample_data()
            cycled = auto_cycle_subscriptions()
            if cycled > 0:
                logger.info(f"Auto-cycled {cycled} subscriptions on startup")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

        # Root layout
        root = BoxLayout(orientation='vertical')

        # Screen manager
        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))
        self.sm.add_widget(DashboardScreen())
        self.sm.add_widget(MembersScreen())
        self.sm.add_widget(PaymentsScreen())
        self.sm.add_widget(CalendarScreen())
        self.sm.add_widget(RemindersScreen())
        self.sm.add_widget(ReportsScreen())
        self.sm.add_widget(MoreScreen())

        root.add_widget(self.sm)

        # Bottom navigation
        self.nav_bar = BottomNavBar(screen_manager=self.sm)
        root.add_widget(self.nav_bar)

        # Sync nav on screen change
        self.sm.bind(current=self._on_screen_change)

        return root

    def _on_screen_change(self, sm, screen_name):
        """Keep nav bar in sync when screens change programmatically."""
        if screen_name in self.nav_bar.buttons:
            for name, btn in self.nav_bar.buttons.items():
                btn.set_active(name == screen_name)

    def on_stop(self):
        """Clean up on app exit."""
        from database.db import db
        db.close()
        logger.info("App stopped, database connection closed")


if __name__ == "__main__":
    MessManagerApp().run()
