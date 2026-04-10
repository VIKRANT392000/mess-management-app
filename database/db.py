"""
SQLite database connection manager (singleton pattern).
"""

import sqlite3
import os
from utils.constants import DB_NAME
from utils.logger import logger


class DatabaseManager:
    """Singleton database connection manager."""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            try:
                db_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), DB_NAME
                )
                self._connection = sqlite3.connect(db_path)
                self._connection.row_factory = sqlite3.Row
                self._connection.execute("PRAGMA journal_mode=WAL")
                self._connection.execute("PRAGMA foreign_keys=ON")
                logger.info(f"Database connected: {db_path}")
            except sqlite3.Error as e:
                logger.error(f"Database connection error: {e}")
                raise
        return self._connection

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        try:
            conn = self.get_connection()
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Query error: {e}\nQuery: {query}\nParams: {params}")
            raise

    def execute_many(self, query: str, params_list: list) -> None:
        """Execute a query with multiple parameter sets."""
        try:
            conn = self.get_connection()
            conn.executemany(query, params_list)
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"ExecuteMany error: {e}\nQuery: {query}")
            raise

    def fetch_one(self, query: str, params: tuple = ()) -> dict:
        """Fetch a single row as dict."""
        try:
            conn = self.get_connection()
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            logger.error(f"FetchOne error: {e}")
            raise

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        """Fetch all rows as list of dicts."""
        try:
            conn = self.get_connection()
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"FetchAll error: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")


# Global instance
db = DatabaseManager()
