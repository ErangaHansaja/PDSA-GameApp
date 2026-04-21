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

def test_initialization_creates_tables(self):
        # Explicitly open and close the connection for the test
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # CRITICAL: Close the connection so tearDown can delete the file!
        conn.close()

        self.assertIn("Player_Responses", tables)
        self.assertIn("Solutions", tables)

    def test_save_and_get_player_response(self):
        self.db.save_player_response("Malinda", "0-0,1-2,2-4")
        count = self.db.get_player_solution_count()
        self.assertEqual(count, 1)

    def test_unique_constraint_on_answer(self):
        self.db.save_player_response("Player1", "0-0,1-2")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.save_player_response("Player2", "0-0,1-2")

    def test_clear_player_responses(self):
        self.db.save_player_response("Yash", "0-0,1-2")
        self.db.clear_player_responses()
        count = self.db.get_player_solution_count()
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
