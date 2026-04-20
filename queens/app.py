import tkinter as tk
from tkinter import messagebox
import sqlite3
from database import DatabaseManager
from logic import NQueensLogic

MAX_SOLUTIONS = 30


class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("16 Queens Puzzle")

        self.root.geometry("1100x800")

        self.db = DatabaseManager()
        self.logic = NQueensLogic(16)
        self.selected_queens = []

        self.setup_ui()


# edit
