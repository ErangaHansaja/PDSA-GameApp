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

    def on_click(self, r, c):
        pos = (r, c)

        if pos in self.selected_queens:
            self.selected_queens.remove(pos)
            color = "#eeeeee" if (r + c) % 2 == 0 else "#666666"
            self.btns[r][c].config(text="", bg=color)

        elif len(self.selected_queens) < 8:
            self.selected_queens.append(pos)
            self.btns[r][c].config(text="♛", bg="#ff4d4d", fg="white")

            if len(self.selected_queens) == 8:
                messagebox.showinfo("Done", "All 8 queens placed!")

        else:
            messagebox.showwarning("Limit", "You can only place 8 queens!")

        self.counter_label.config(text=f"Queens: {len(self.selected_queens)}/8")

    def check(self):
        name = self.name_entry.get().strip()

        if not name:
            messagebox.showwarning("Error", "Enter your name!")
            return

        if len(self.selected_queens) != 8:
            messagebox.showwarning("Error", "Place exactly 8 queens!")
            return

        if not self.logic.is_valid(self.selected_queens):
            messagebox.showerror("Invalid", "Queens attack each other!")
            return

        answer = ",".join([f"{r}-{c}" for r, c in sorted(self.selected_queens)])

        try:
            self.db.save_player_response(name, answer)
            messagebox.showinfo("Success", "Saved!")
            self.reset_board()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate", "Solution already exists!")
            return

        # Check AFTER insert
        current = self.db.get_player_solution_count()

        if current >= MAX_SOLUTIONS:
            self.show_clear_flag_popup()
