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
