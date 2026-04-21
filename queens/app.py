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

     def setup_ui(self):
        self.root.configure(bg="#1e1e1e")

        title = tk.Label(
            self.root,
            text="♛ Sixteen Queens Puzzle ♛",
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#1e1e1e",
        )
        title.pack(pady=10)

        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack()

        tk.Label(frame, text="Name:", fg="white", bg="#1e1e1e").pack(side=tk.LEFT)

        self.name_entry = tk.Entry(frame, bg="#2b2b2b", fg="white")
        self.name_entry.pack(side=tk.LEFT, padx=10)

        self.counter_label = tk.Label(
            self.root,
            text="Queens: 0/8",
            font=("Helvetica", 12, "bold"),
            fg="white",
            bg="#1e1e1e",
        )
        self.counter_label.pack()

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=10)

        self.btns = [[None for _ in range(16)] for _ in range(16)]

        for r in range(16):
            for c in range(16):
                color = "#eeeeee" if (r + c) % 2 == 0 else "#666666"

                btn = tk.Button(
                    self.grid_frame,
                    width=3,
                    height=1,
                    font=("Arial", 14, "bold"),
                    bg=color,
                    activebackground=color,
                    relief="flat",
                    command=lambda r=r, c=c: self.on_click(r, c),
                )
                btn.grid(row=r, column=c)
                self.btns[r][c] = btn

        bottom = tk.Frame(self.root, bg="#1e1e1e")
        bottom.pack(pady=10)

        tk.Button(
            bottom, text="CHECK", bg="#28a745", fg="white", command=self.check
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            bottom,
            text="PERFORMANCE",
            bg="#007bff",
            fg="white",
            command=self.performance,
        ).pack(side=tk.LEFT, padx=10)


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

 def performance(self):
        demo = NQueensLogic(16, max_solutions=MAX_SOLUTIONS)

        s_count, s_time, s_solutions = demo.run_sequential()
        t_count, t_time, t_solutions = demo.run_threaded()

        self.db.save_performance_stats(s_count, t_count, s_time, t_time)

        # Save all unique solutions
        all_solutions = set(map(str, s_solutions + t_solutions))

        for sol in all_solutions:
            try:
                self.db.save_solution(sol)
            except:
                pass

        faster = "Sequential" if s_time < t_time else "Threaded"

        messagebox.showinfo(
            "Performance",
            f"Sequential: {s_time:.4f}s\nThreaded: {t_time:.4f}s\nFaster: {faster}",
        )

    def show_clear_flag_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Max Solutions Reached")
        popup.geometry("300x150")
        popup.configure(bg="#1e1e1e")

        tk.Label(
            popup,
            text="30 solutions reached!\nYou can now reset the system.",
            fg="white",
            bg="#1e1e1e",
            font=("Helvetica", 11),
        ).pack(pady=20)

        def clear_flag():
            self.db.clear_player_responses()
            messagebox.showinfo("Cleared", "Player responses reset!")
            popup.destroy()

        tk.Button(
            popup,
            text="Clear Flag",
            bg="#dc3545",
            fg="white",
            command=clear_flag,
            width=15,
        ).pack(pady=10)

    def reset_board(self):
        # Clear selected queens
        self.selected_queens.clear()

        # Reset all buttons
        for r in range(16):
            for c in range(16):
                color = "#eeeeee" if (r + c) % 2 == 0 else "#666666"
                self.btns[r][c].config(text="", bg=color)

        # Reset counter
        self.counter_label.config(text="Queens: 0/8")

        # Clear name field
        self.name_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
