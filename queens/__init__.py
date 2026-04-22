import tkinter as tk
from queens.app import ChessApp


def open_queens_game(parent):
    window = tk.Toplevel(parent)
    ChessApp(window)
