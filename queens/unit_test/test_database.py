import unittest
import sqlite3
import os
import time
from database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_chess.db"

        # Ensure a completely clean slate before the test starts
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass

        self.db = DatabaseManager(self.test_db)

    def tearDown(self):
        # Give SQLite a tiny fraction of a second to release file locks
        time.sleep(0.1)
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                print(
                    f"\nWarning: Could not remove {self.test_db}. A connection might still be open."
                )
