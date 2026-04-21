import unittest
import tkinter as tk
from app import ChessApp


class TestChessApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a single hidden root window for all UI tests
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Initialize the app before each test
        self.app = ChessApp(self.root)
        # Point the app to a test database so UI tests don't hit production DB
        self.app.db.db_name = "test_ui_chess.db"
        self.app.db.init_db()

    def test_initial_state(self):
        # Check initial variables
        self.assertEqual(len(self.app.selected_queens), 0)
        self.assertEqual(self.app.counter_label.cget("text"), "Queens: 0/8")

    def test_on_click_adds_queen(self):
        # Simulate clicking row 0, col 0
        self.app.on_click(0, 0)
        self.assertIn((0, 0), self.app.selected_queens)
        self.assertEqual(self.app.counter_label.cget("text"), "Queens: 1/8")

    def test_on_click_removes_queen(self):
        # Simulate clicking twice to add then remove
        self.app.on_click(2, 2)
        self.app.on_click(2, 2)
        self.assertNotIn((2, 2), self.app.selected_queens)
        self.assertEqual(self.app.counter_label.cget("text"), "Queens: 0/8")


if __name__ == "__main__":
    unittest.main()


