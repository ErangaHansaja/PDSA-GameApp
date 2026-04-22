"""app.py – Tkinter GUI for Knight's Tour Player enters their name on the Start screen; it is saved to SQLite on a win."""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time

from database.knightstour import init_db, save_winner, fetch_winners, save_algorithm_time
from knightstour.knight_logic import (
    get_valid_moves,
    is_valid_knight_move,
    validate_tour,
    BruteForce,
    solve_backtracking,
    solve_warnsdorff,
    solve_parberry,
)

class KnightsTourApp(tk.Tk):
    def __init__(self):
        super().__init__()
        if init_db() == -1:
            messagebox.showerror("Database Error")
            self.destroy()
        self.title("♞ Knight's Tour Problem")
        self.resizable(True, True)
        self.configure(bg="#0f0f1a")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.center_x = (self.screen_width // 2)
        self.center_y = (self.screen_height // 2)
        print(f"Screen size: {self.screen_width}x{self.screen_height}")
        # Round tracking variables
        self._current_round = 0
        self._total_rounds = 20
        self._round_scores = []  # List of tuples: (round_num, board_size, moves, start_pos)
        # Algorithm timing variables
        self._bt_time = 0.0
        self._warn_time = 0.0
        self._parberry_time = 0.0
        self._setup_styles()
        self._show_menu()

    # ── styles 

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame",  background="#0f0f1a")
        style.configure("TLabel",  background="#0f0f1a", foreground="#e8e0d0",
                        font=("Georgia", 12))
        style.configure("Title.TLabel", font=("Georgia", 28, "bold"),
                        foreground="#f5c842")
        style.configure("Sub.TLabel",   font=("Georgia", 13),
                        foreground="#a09880")
        style.configure("TButton",
                        background="#2a2a3e", foreground="#f5c842",
                        font=("Georgia", 12, "bold"),
                        borderwidth=1, relief="flat", padding=8)
        style.map("TButton",
                  background=[("active", "#3a3a5e")],
                  foreground=[("active", "#ffffff")])
        style.configure("Accent.TButton",
                        background="#f5c842", foreground="#0f0f1a",
                        font=("Georgia", 13, "bold"), padding=10)
        style.map("Accent.TButton",
                  background=[("active", "#d4a820")])

    # ── helpers  

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _get_algorithm_used(self):
        """Determine which algorithm the player's tour matches."""
        if self._sequence == self._bf_solution:
            return "Backtracking"
        elif self._sequence == self._warn_solution:
            return "Warnsdorff's Rule"
        else:
            return "Player"

    
    #  MAIN MENU  (includes player name entry)
     

    def _show_menu(self):
        self._current_round = 0
        self._round_scores = []
        self._clear()
        self.geometry(f"560x580+{self.center_x - 280}+{self.center_y - 290}")

        f = ttk.Frame(self, padding=40)
        f.pack(expand=True, fill="both")

        ttk.Label(f, text="♞", font=("Georgia", 64), foreground="#f5c842",
                  background="#0f0f1a").pack(pady=(10, 0))
        ttk.Label(f, text="Knight's Tour", style="Title.TLabel").pack()
        ttk.Label(f, text="Traverse every square – exactly once",
                  style="Sub.TLabel").pack(pady=(4, 20))

        # ── Player name  
        name_frame = ttk.Frame(f)
        name_frame.pack(pady=(0, 8))
        ttk.Label(name_frame, text="Your Name:", style="TLabel").pack(side="left", padx=(0, 8))
        self._player_name_var = tk.StringVar()
        name_entry = tk.Entry(
            name_frame,
            textvariable=self._player_name_var,
            bg="#1e1e30", fg="#f5c842",
            insertbackground="#f5c842",
            font=("Georgia", 12),
            relief="flat", bd=2,
            highlightthickness=1,
            highlightbackground="#3a3a5e",
            highlightcolor="#f5c842",
            width=20,
        )
        name_entry.pack(side="left")
        name_entry.focus_set()

        # ── Board size  
        ttk.Label(f, text="Select Board Size:", style="TLabel").pack(pady=(12, 0))
        self._size_var = tk.IntVar(value=8)
        sf = ttk.Frame(f)
        sf.pack(pady=8)
        for sz, lbl in [(8, "8 × 8  (Standard)"), (16, "16 × 16  (Expert)")]:
            tk.Radiobutton(
                sf, text=lbl, variable=self._size_var, value=sz,
                bg="#0f0f1a", fg="#e8e0d0", selectcolor="#2a2a3e",
                activebackground="#0f0f1a", activeforeground="#f5c842",
                font=("Georgia", 12), indicatoron=True,
            ).pack(side="left", padx=16)

        ttk.Button(f, text="▶  Start Game",
                   command=self._start_game, style="Accent.TButton").pack(pady=20, ipadx=20)
        '''ttk.Button(f, text="📊  Dashboard",
                   command=self._show_dashboard).pack(pady=4)'''
        ttk.Button(f, text="🏆  View Winners",
                   command=self._show_leaderboard).pack(pady=4)
        ttk.Button(f, text="📊  Dashboard",
                   command=self._show_dashboard).pack(pady=4)

    def _show_dashboard(self):
        pass
    #  GAME SCREEN
     

    def _start_game(self):
        # Validate player name
        player_name = self._player_name_var.get().strip()
        if player_name.isnumeric():
            messagebox.showwarning("Invalid Name", "Name cannot be purely numeric. Please enter a valid name!")
            return
        if not player_name:
            messagebox.showwarning("Name Required", "Please enter your name before starting!")
            return

        self._player_name = player_name
        self._current_round += 1
        self._clear()
        self._size      = self._size_var.get()
        self._cells     = {}
        self._sequence  = []
        self._game_over = False
        self._start_selected = False

        self._start = None

        self._bf_solution   = []
        self._warn_solution = []
        self._parberry_solution = []

        if self._size == 8:
            cell = 48
        else:
            cell = 37
        self._cell_px = cell
        board_px = cell * self._size

        self.geometry(f"1100x800+{self.center_x - 550}+{self.center_y - 400}")

        # ── top bar 
        top = tk.Frame(self, bg="#0f0f1a")
        top.pack(fill="x", padx=16, pady=8)
        tk.Label(top, text=f"♞ Knight's Tour  –  {self._player_name}  |  Round {self._current_round}/{self._total_rounds}",
                 bg="#0f0f1a", fg="#f5c842",
                 font=("Georgia", 18, "bold")).pack(side="left")
        tk.Button(top, text="☰ Menu",
                  command=self._show_menu,
                  bg="#2a2a3e", fg="#f5c842",
                  font=("Georgia", 11, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  padx=10).pack(side="right")

        # ── main area 
        main = tk.Frame(self, bg="#0f0f1a")
        main.pack(fill="both", expand=True, padx=16, pady=4)

        self._canvas = tk.Canvas(
            main, width=board_px, height=board_px,
            bg="#1a1a2e", highlightthickness=2,
            highlightbackground="#f5c842",
        )
        self._canvas.pack(side="left")
        self._canvas.bind("<Button-1>", self._on_click)

        side = tk.Frame(main, bg="#0f0f1a", width=300)
        side.pack(side="left", fill="both", expand=True, padx=(16, 0))

        tk.Label(side, text=f"Board: {self._size}×{self._size}",
                 bg="#0f0f1a", fg="#a09880", font=("Georgia", 11)).pack(anchor="w")
        self._start_lbl = tk.Label(
            side, text="Start: (select by clicking)",
            bg="#0f0f1a", fg="#f5c842", font=("Georgia", 11, "bold"))
        self._start_lbl.pack(anchor="w", pady=2)

        self._moves_lbl = tk.Label(
            side, text="Moves: 0 / " + str(self._size ** 2),
            bg="#0f0f1a", fg="#e8e0d0", font=("Georgia", 11))
        self._moves_lbl.pack(anchor="w", pady=2)

        self._progress = ttk.Progressbar(
            side, orient="horizontal", length=260,
            mode="determinate", maximum=self._size ** 2)
        self._progress.pack(anchor="w", pady=6)

        self._status_lbl = tk.Label(
            side, text="Click any square to select your starting position!",
            bg="#0f0f1a", fg="#78c8a0",
            font=("Georgia", 11), wraplength=270, justify="left")
        self._status_lbl.pack(anchor="w", pady=4)

        tk.Label(side, text="Valid next moves are highlighted in green.",
                 bg="#0f0f1a", fg="#606070", font=("Georgia", 9),
                 wraplength=270).pack(anchor="w", pady=2)

        tk.Frame(side, bg="#2a2a3e", height=1).pack(fill="x", pady=10)

        tk.Button(side, text="↩  Undo Last Move", command=self._undo,
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  cursor="hand2", padx=8, pady=6).pack(fill="x", pady=3)
        tk.Button(side, text="✓  Submit Tour", command=self._submit,
                  bg="#f5c842", fg="#0f0f1a",
                  font=("Georgia", 12, "bold"), relief="flat", bd=0,
                  cursor="hand2", padx=8, pady=8).pack(fill="x", pady=3)
        tk.Button(side, text="⟳  New Game", command=self._new_game,
                  bg="#2a2a3e", fg="#f5c842",
                  font=("Georgia", 11), relief="flat", bd=0,
                  cursor="hand2", padx=8, pady=6).pack(fill="x", pady=3)
        tk.Button(side, text="💡  Show Solution", command=self._show_solution_dialog,
                  bg="#2a2a3e", fg="#a09880",
                  font=("Georgia", 11), relief="flat", bd=0,
                  cursor="hand2", padx=8, pady=6).pack(fill="x", pady=3)

        tk.Frame(side, bg="#2a2a3e", height=1).pack(fill="x", pady=10)

        tk.Label(side, text="Move History",
                 bg="#0f0f1a", fg="#a09880",
                 font=("Georgia", 10)).pack(anchor="w")
        self._history_box = tk.Listbox(
            side, bg="#12121f", fg="#c8c0b0",
            font=("Courier", 9), height=10,
            selectbackground="#2a2a3e",
            highlightthickness=0, bd=0)
        self._history_box.pack(fill="both", expand=True, pady=4)

        self._draw_board()

    def _new_game(self):
        """Restart with the same player name – skip the menu."""
        # Keep _player_name_var consistent so _start_game can read it
        if not hasattr(self, "_size_var"):
            self._size_var = tk.IntVar(value=8)
        # Temporarily set name var so validation passes
        if not hasattr(self, "_player_name_var"):
            self._player_name_var = tk.StringVar()
        self._player_name_var.set(getattr(self, "_player_name", "Player"))
        # Reset round counter for a new tournament
        self._current_round = 0
        self._round_scores = []
        self._start_game()

    def _run_solvers(self):
        try:
            start = time.time()
            self._bf_solution = []
            self._bf_solution = solve_backtracking(self._start, self._size)
            self._bf_time = time.time() - start
            # Save brute force timing to database
            try:
                save_algorithm_time(self._player_name, self._current_round, "Brute Force", 
                                  self._size, self._bf_time * 1000)
            except Exception as db_err:
                print(f"Error saving brute force time: {db_err}")
        except Exception:
            self._bf_solution = []
            self._bf_time = 0.0
        try:
            start = time.time()
            self._warn_solution = solve_warnsdorff(self._start, self._size)
            self._warn_time = time.time() - start
            # Save Warnsdorff timing to database
            try:
                save_algorithm_time(self._player_name, self._current_round, "Warnsdorff", 
                                  self._size, self._warn_time * 1000)
            except Exception as db_err:
                print(f"Error saving Warnsdorff time: {db_err}")
        except Exception:
            self._warn_solution = []
            self._warn_time = 0.0
        try:
            # Use Parberry for 16×16, fallback to Warnsdorff for 8×8
            start = time.time()
            self._parberry_solution = solve_parberry(self._start, self._size)
            self._parberry_time = time.time() - start
            # Save Parberry timing to database
            try:
                save_algorithm_time(self._player_name, self._current_round, "Parberry", 
                                  self._size, self._parberry_time * 1000)
            except Exception as db_err:
                print(f"Error saving Parberry time: {db_err}")
        except Exception:
            self._parberry_solution = []
            self._parberry_time = 0.0

    # board drawing  

    def _draw_board(self):
        self._canvas.delete("all")
        self._cells = {}
        cell = self._cell_px
        for r in range(self._size):
            for c in range(self._size):
                x0, y0 = c * cell, r * cell
                x1, y1 = x0 + cell, y0 + cell
                base = "#c8b080" if (r + c) % 2 == 0 else "#5a3e28"
                rect = self._canvas.create_rectangle(
                    x0, y0, x1, y1, fill=base, outline="#0f0f1a", width=1)
                self._cells[(r, c)] = rect
        if self._start_selected:
            self._highlight_start()

    def _draw_solution_board(self, canvas, solution):
        """Draw the complete solution board (non-animated)."""
        canvas.delete("all")
        self._cells = {}
        cell = self._cell_px

        for r in range(self._size):
            for c in range(self._size):
                x0, y0 = c * cell, r * cell
                x1, y1 = x0 + cell, y0 + cell
                base = "#c8b080" if (r + c) % 2 == 0 else "#5a3e28"
                rect = canvas.create_rectangle(
                    x0, y0, x1, y1, fill=base, outline="#0f0f1a", width=1)
                self._cells[(r, c)] = rect

        for i, pos in enumerate(solution):
            r, c = pos
            x = c * cell + cell // 2
            y = r * cell + cell // 2
            canvas.create_rectangle(
                c * cell, r * cell, (c + 1) * cell, (r + 1) * cell,
                fill="#2a6a40", outline="#1f4e28", width=2)
            canvas.create_text(
                x, y, text=str(i + 1),
                fill="#ffffff", font=("Georgia", max(7, cell // 4), "bold"))

    def _animate_solution_board(self, canvas, solution, delay_ms=50):
        """Animate the solution board by drawing moves one at a time."""
        canvas.delete("all")
        cell = self._cell_px

        for r in range(self._size):
            for c in range(self._size):
                x0, y0 = c * cell, r * cell
                x1, y1 = x0 + cell, y0 + cell
                base = "#c8b080" if (r + c) % 2 == 0 else "#5a3e28"
                rect = canvas.create_rectangle(
                    x0, y0, x1, y1, fill=base, outline="#0f0f1a", width=1)
                self._cells[(r, c)] = rect
        
        def draw_step(step):
            if step < len(solution):
                i = step
                pos = solution[i]
                r, c = pos
                x = c * cell + cell // 2
                y = r * cell + cell // 2
                
                # Draw cell with gradient coloring based on position in sequence
                frac = i / max(len(solution) - 1, 1)
                g = int(60 + frac * 80)
                color = f"#2a{g:02x}60"
                
                canvas.create_rectangle(
                    c * cell, r * cell, (c + 1) * cell, (r + 1) * cell,
                    fill=color, outline="#1f4e28", width=2)
                canvas.create_text(
                    x, y, text=str(i + 1),
                    fill="#ffffff", font=("Georgia", max(7, cell // 4), "bold"))
                
                # Schedule next step
                canvas.after(delay_ms, draw_step, step + 1)
        
        draw_step(0)

    def _highlight_start(self):
        r, c = self._start
        cell = self._cell_px
        x0, y0 = c * cell, r * cell
        x1, y1 = x0 + cell, y0 + cell
        self._canvas.create_oval(
            x0 + 4, y0 + 4, x1 - 4, y1 - 4,
            fill="#f5c842", outline="#c89010", width=2,
            tags="start_marker")

    def _refresh_board(self):
        cell = self._cell_px
        valid_next = set()
        if self._sequence and not self._game_over:
            valid_next = {
                m for m in get_valid_moves(self._sequence[-1], self._size)
                if m not in self._sequence
            }

        for r in range(self._size):
            for c in range(self._size):
                pos = (r, c)
                base = "#c8b080" if (r + c) % 2 == 0 else "#5a3e28"
                if not self._sequence:
                    color = base
                elif pos == self._sequence[0]:
                    color = "#f5c842"
                elif pos in self._sequence[1:]:
                    idx = self._sequence.index(pos)
                    frac = idx / max(len(self._sequence) - 1, 1)
                    g = int(60 + frac * 80)
                    color = f"#20{g:02x}50"
                elif pos in valid_next:
                    color = "#2a6a40"
                else:
                    color = base
                self._canvas.itemconfig(self._cells[pos], fill=color)

        self._canvas.delete("label")
        for i, pos in enumerate(self._sequence):
            r, c = pos
            x = c * cell + cell // 2
            y = r * cell + cell // 2
            self._canvas.create_text(
                x, y, text=str(i + 1),
                fill="#ffffff" if i > 0 else "#0f0f1a",
                font=("Georgia", max(7, cell // 4), "bold"),
                tags="label")

        self._canvas.delete("knight")
        if self._sequence:
            r, c = self._sequence[-1]
            x = c * cell + cell // 2
            y = r * cell + cell // 2
            self._canvas.create_text(
                x, y - 2, text="♞",
                font=("Segoe UI Symbol", max(10, cell // 3)),
                fill="#fffbe0", tags="knight")

    # ── click handler 

    def _on_click(self, event):
        if self._game_over:
            return
        cell = self._cell_px
        c = event.x // cell
        r = event.y // cell
        if not (0 <= r < self._size and 0 <= c < self._size):
            return
        pos = (r, c)

        # If starting position hasn't been selected yet, allow player to select it
        if len(self._sequence) == 0:
            self.start_time = time.time()
            self._start = pos
            self._start_selected = True
            self._start_lbl.config(text=f"Start: {self._start}")
            self._set_status(f"✓ Starting position set to {self._start}. Begin your tour!",
                            "#78c8a0")
            # Run solvers in background now that start position is known
            threading.Thread(target=self._run_solvers, daemon=True).start()
            self._sequence.append(pos)
            self._history_box.insert("end", f" 1. {pos}  ← Start")
            self._moves_lbl.config(text=f"Moves: {len(self._sequence)} / {self._size ** 2}")
            self._progress["value"] = len(self._sequence)
            self._refresh_board()
            return

        # Normal move handling after start position is selected
        last = self._sequence[-1]
        if pos in self._sequence:
            self._set_status("⚠ Square already visited!", "#e86040")
            return
        if not is_valid_knight_move(last, pos):
            self._set_status(
                f"⚠ Invalid knight move from {last} to {pos}.", "#e86040")
            return
        self._sequence.append(pos)
        n = len(self._sequence)
        self._history_box.insert("end", f" {n}. {pos}")
        self._history_box.see("end")

        self._moves_lbl.config(text=f"Moves: {len(self._sequence)} / {self._size ** 2}")
        self._progress["value"] = len(self._sequence)
        remaining = self._size ** 2 - len(self._sequence)
        self._set_status(
            f"✓ Move {len(self._sequence)} recorded.  {remaining} squares left.",
            "#78c8a0")
        self._refresh_board()

        if len(self._sequence) == self._size ** 2:
            self._submit()

    # ── undo 

    def _undo(self):
        if self._game_over or not self._sequence:
            return
        if len(self._sequence) > 0:
            self._sequence.pop()
            last_idx = self._history_box.size() - 1
            if last_idx >= 0:
                self._history_box.delete(last_idx)
            self._moves_lbl.config(text=f"Moves: {len(self._sequence)} / {self._size ** 2}")
            self._progress["value"] = len(self._sequence)
            self._set_status("↩ Last move undone.", "#a09880")
            self._refresh_board()

    # ── submit 

    def _submit(self):
        if self._game_over:
            return
        if len(self._sequence) < self._size ** 2:
            ans = messagebox.askyesno(
                "Incomplete Tour",
                f"You've only visited {len(self._sequence)} of "
                f"{self._size ** 2} squares.\nSubmit anyway (this will count as a loss)?")
            if not ans:
                return

        valid, msg = validate_tour(self._sequence, self._size)
        self._game_over = True
        self._refresh_board()

        if valid:
            # Automatically save the score when a valid tour is submitted
            try:
                self.end_time = time.time()
                self.total_time = self.end_time - self.start_time
                self._show_win_dialog(msg)
            except RuntimeError as e:
                messagebox.showerror("DB Error", str(e))
            self._show_win_dialog(msg)
        else:
            self._show_result_dialog("😞 Incomplete Tour", msg, win=False)

    # ── result dialogs 

    def _show_win_dialog(self, msg):
        win = tk.Toplevel(self)
        win.title("🏆 You Won!")
        win.configure(bg="#0f0f1a")
        win.geometry(f"420x420+{self.center_x - 210}+{self.center_y - 210}")
        win.grab_set()

        tk.Label(win, text="🏆", font=("Georgia", 48),
                 bg="#0f0f1a", fg="#f5c842").pack(pady=(20, 0))
        tk.Label(win, text="Congratulations!",
                 bg="#0f0f1a", fg="#f5c842",
                 font=("Georgia", 20, "bold")).pack()
        tk.Label(win, text=msg,
                 bg="#0f0f1a", fg="#78c8a0",
                 font=("Georgia", 11)).pack(pady=4)
        tk.Label(
            win,
            text=f"Player: {self._player_name}\n"
                 f"Round: {self._current_round}/{self._total_rounds}\n"
                 f"Completed {self._size}×{self._size} board\n"
                 f"from {self._start} in {len(self._sequence)} moves.",
            bg="#0f0f1a", fg="#e8e0d0",
            font=("Georgia", 11)).pack(pady=4)

        # Store round score
        self._round_scores.append({
            'round': self._current_round,
            'board_size': self._size,
            'moves': len(self._sequence),
            'start': self._start
        })

        def save_and_close():
            try:
                save_winner(
                    self._player_name,
                    self._size,
                    self._start,
                    len(self._sequence),
                    self._sequence,
                    self._current_round,
                    self.total_time
                )
                messagebox.showinfo(
                    "Saved",
                    f"{self._player_name}'s score has been saved to the leaderboard!",
                    parent=win,
                )
            except RuntimeError as e:
                messagebox.showerror("DB Error", str(e), parent=win)
            win.destroy()
        
        # Show different buttons based on round count
        if self._current_round < self._total_rounds:
            tk.Button(win, text="▶  Next Round",
                      command=lambda: [win.destroy(), self._start_game()],
                      bg="#2a6a40", fg="#ffffff",
                      font=("Georgia", 11, "bold"), relief="flat", bd=0,
                      padx=10, pady=6).pack(pady=10)
            tk.Button(win, text="💾  Save My Score",
                  command=save_and_close,
                  bg="#2a6a40", fg="#ffffff",
                  font=("Georgia", 11, "bold"), relief="flat", bd=0,
                  padx=10, pady=6).pack(pady=10)

        
        if self._current_round == self._total_rounds:
            tk.Button(win, text="📊  Tournament Summary",
                      command=lambda: [win.destroy(), self._show_tournament_summary()],
                      bg="#2a6a40", fg="#ffffff",
                      font=("Georgia", 11, "bold"), relief="flat", bd=0,
                      padx=10, pady=6).pack(pady=10)
        else:
            tk.Button(win, text="⟳  Play Again",
                      command=lambda: [win.destroy(), self._new_game()],
                      bg="#2a2a3e", fg="#f5c842",
                      font=("Georgia", 11), relief="flat", bd=0,
                      padx=10, pady=6).pack(pady=10)

    def _show_result_dialog(self, title, msg, win=False):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.configure(bg="#0f0f1a")
        dlg.geometry(f"380x240+{self.center_x - 190}+{self.center_y - 120}")
        dlg.grab_set()

        icon  = "🏆" if win else "♞"
        color = "#f5c842" if win else "#e86040"
        tk.Label(dlg, text=icon, font=("Georgia", 40),
                 bg="#0f0f1a", fg=color).pack(pady=(20, 0))
        tk.Label(dlg, text=title, bg="#0f0f1a", fg=color,
                 font=("Georgia", 16, "bold")).pack()
        tk.Label(dlg, text=msg, bg="#0f0f1a", fg="#e8e0d0",
                 font=("Georgia", 11), wraplength=340).pack(pady=8)
        tk.Button(dlg, text="⟳  Try Again",
                  command=lambda: [dlg.destroy(), self._new_game()],
                  bg="#2a2a3e", fg="#f5c842",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(pady=6)
        tk.Button(dlg, text="☰  Main Menu",
                  command=lambda: [dlg.destroy(), self._show_menu()],
                  bg="#2a2a3e", fg="#a09880",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack()

    # ── solution viewer  

    def _show_solution_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("💡 Algorithm Solutions")
        dlg.configure(bg="#0f0f1a")
        dlg.geometry(f"480x520+{self.center_x - 240}+{self.center_y - 260}")
        dlg.grab_set()

        tk.Label(dlg, text="Algorithm Solutions",
                 bg="#0f0f1a", fg="#f5c842",
                 font=("Georgia", 16, "bold")).pack(pady=(16, 4))
        tk.Label(
            dlg,
            text="These are the reference solutions computed silently.\n"
                 "Your tour is valid as long as it follows the rules.",
            bg="#0f0f1a", fg="#a09880",
            font=("Georgia", 10), wraplength=440).pack()

        nb = ttk.Notebook(dlg)
        nb.pack(fill="both", expand=True, padx=12, pady=8)

        # Backtracking tab
        bt_frame = tk.Frame(nb, bg="#12121f")
        nb.add(bt_frame, text="Backtracking")
        if not self._bf_solution:
            tk.Label(bt_frame,
                     text="Solution still computing or not found.",
                     bg="#12121f", fg="#e86040",
                     font=("Georgia", 11)).pack(pady=20)
        else:
            tk.Label(bt_frame,
                     text=f"⏱ Execution Time: {self._bt_time*1000:.2f} ms",
                     bg="#12121f", fg="#78c8a0",
                     font=("Georgia", 10, "bold")).pack(pady=(8, 4))
            sb = tk.Scrollbar(bt_frame)
            sb.pack(side="right", fill="y")
            lb = tk.Listbox(bt_frame, yscrollcommand=sb.set,
                            bg="#12121f", fg="#c8c0b0",
                            font=("Courier", 9),
                            highlightthickness=0, bd=0)
            lb.pack(fill="both", expand=True)
            sb.config(command=lb.yview)
            for i, pos in enumerate(self._bf_solution):
                lb.insert("end", f"  {i + 1:3d}.  {pos}")
        
        # Warnsdorff tab
        warn_frame = tk.Frame(nb, bg="#12121f")
        nb.add(warn_frame, text="Warnsdorff")
        if not self._warn_solution:
            tk.Label(warn_frame,
                     text="Solution still computing or not found.",
                     bg="#12121f", fg="#e86040",
                     font=("Georgia", 11)).pack(pady=20)
        else:
            tk.Label(warn_frame,
                     text=f"⏱ Execution Time: {self._warn_time*1000:.2f} ms",
                     bg="#12121f", fg="#78c8a0",
                     font=("Georgia", 10, "bold")).pack(pady=(8, 4))
            sb = tk.Scrollbar(warn_frame)
            sb.pack(side="right", fill="y")
            lb = tk.Listbox(warn_frame, yscrollcommand=sb.set,
                            bg="#12121f", fg="#c8c0b0",
                            font=("Courier", 9),
                            highlightthickness=0, bd=0)
            lb.pack(fill="both", expand=True)
            sb.config(command=lb.yview)
            for i, pos in enumerate(self._warn_solution):
                lb.insert("end", f"  {i + 1:3d}.  {pos}")
        
        # Parberry tab (for 16×16 boards)
        if self._size == 16:
            parberry_frame = tk.Frame(nb, bg="#12121f")
            nb.add(parberry_frame, text="Parberry (D&C)")
            if not self._parberry_solution:
                tk.Label(parberry_frame,
                         text="Solution still computing or not found.",
                         bg="#12121f", fg="#e86040",
                         font=("Georgia", 11)).pack(pady=20)
            else:
                tk.Label(parberry_frame,
                         text=f"⏱ Execution Time: {self._parberry_time*1000:.2f} ms",
                         bg="#12121f", fg="#78c8a0",
                         font=("Georgia", 10, "bold")).pack(pady=(8, 4))
                sb = tk.Scrollbar(parberry_frame)
                sb.pack(side="right", fill="y")
                lb = tk.Listbox(parberry_frame, yscrollcommand=sb.set,
                                bg="#12121f", fg="#c8c0b0",
                                font=("Courier", 9),
                                highlightthickness=0, bd=0)
                lb.pack(fill="both", expand=True)
                sb.config(command=lb.yview)
                for i, pos in enumerate(self._parberry_solution):
                    lb.insert("end", f"  {i + 1:3d}.  {pos}")

        btn_frame = tk.Frame(dlg, bg="#0f0f1a")
        btn_frame.pack(pady=8, anchor="center")
        
        tk.Button(btn_frame, text="▶ Backtracking Path", 
                  command=self._show_backtracking_path,
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)
        
        tk.Button(btn_frame, text="▶ Warnsdorff Path", 
                  command=self._show_warnsdorff_path,
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)
        
        if self._size == 16:
            tk.Button(btn_frame, text="▶ Parberry Path", 
                      command=self._show_parberry_path,
                      bg="#2a2a3e", fg="#e8e0d0",
                      font=("Georgia", 11), relief="flat", bd=0,
                      padx=10, pady=6).pack(side="left", padx=4)
        
        tk.Button(dlg, text="Close", command=dlg.destroy,
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(pady=8)

    def _show_warnsdorff_path(self):
        dlg = tk.Toplevel(self)
        dlg.title(f"Warnsdorff's Rule Path (⏱ {self._warn_time*1000:.2f} ms)")
        dlg.configure(bg="#0f0f1a")
        board_size = self._cell_px * self._size
        dlg.geometry(f"{board_size + 40}x{board_size + 100}+{self.center_x - (board_size + 40)//2}+{self.center_y - (board_size + 100)//2}")
        dlg.grab_set()
        
        canvas_frame = tk.Frame(dlg, bg="#0f0f1a")
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="#0f0f1a", width=self._cell_px * self._size, height=self._cell_px * self._size, highlightthickness=0)
        canvas.pack(anchor="center")
        
        # Start animation immediately
        self._animate_solution_board(canvas, self._warn_solution, delay_ms=50)
        
        btn_frame = tk.Frame(dlg, bg="#0f0f1a")
        btn_frame.pack(pady=8, anchor="center")
        
        tk.Button(btn_frame, text="▶ Replay Animation", 
                  command=lambda: self._animate_solution_board(canvas, self._warn_solution, delay_ms=50),
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)
        
        tk.Button(btn_frame, text="⏸ Show Full Path", 
                  command=lambda: self._draw_solution_board(canvas, self._warn_solution),
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)
        
        tk.Button(btn_frame, text="Close", command=dlg.destroy,
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)

    def _show_backtracking_path(self):
        dlg = tk.Toplevel(self)
        dlg.title(f"Backtracking Path (⏱ {self._bt_time*1000:.2f} ms)")
        dlg.configure(bg="#0f0f1a")
        board_size = self._cell_px * self._size
        dlg.geometry(f"{board_size + 40}x{board_size + 100}+{self.center_x - (board_size + 40)//2}+{self.center_y - (board_size + 100)//2}")
        dlg.grab_set()
        
        canvas_frame = tk.Frame(dlg, bg="#0f0f1a")
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="#0f0f1a", width=self._cell_px * self._size, height=self._cell_px * self._size, highlightthickness=0)
        canvas.pack(anchor="center")
        
        # Start animation immediately
        self._animate_solution_board(canvas, self._bf_solution, delay_ms=50)
        
        btn_frame = tk.Frame(dlg, bg="#0f0f1a")
        btn_frame.pack(pady=8, anchor="center")
        
        tk.Button(btn_frame, text="▶ Replay Animation", 
                  command=lambda: self._animate_solution_board(canvas, self._bf_solution, delay_ms=50),
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)
        
        tk.Button(btn_frame, text="⏸ Show Full Path", 
                  command=lambda: self._draw_solution_board(canvas, self._bf_solution),
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)
        
        tk.Button(btn_frame, text="Close", command=dlg.destroy,
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)

    def _show_parberry_path(self):
        dlg = tk.Toplevel(self)
        dlg.title(f"Parberry Divide & Conquer Path (⏱ {self._parberry_time*1000:.2f} ms)")
        dlg.configure(bg="#0f0f1a")
        board_size = self._cell_px * self._size
        dlg.geometry(f"{board_size + 40}x{board_size + 100}+{self.center_x - (board_size + 40)//2}+{self.center_y - (board_size + 100)//2}")
        dlg.grab_set()
        
        canvas_frame = tk.Frame(dlg, bg="#0f0f1a")
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="#0f0f1a", width=self._cell_px * self._size, height=self._cell_px * self._size, highlightthickness=0)
        canvas.pack(anchor="center")
        
        # Start animation immediately
        self._animate_solution_board(canvas, self._parberry_solution, delay_ms=30)
        
        btn_frame = tk.Frame(dlg, bg="#0f0f1a")
        btn_frame.pack(pady=8, anchor="center")
        
        tk.Button(btn_frame, text="▶ Replay Animation", 
                  command=lambda: self._animate_solution_board(canvas, self._parberry_solution, delay_ms=30),
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)
        
        tk.Button(btn_frame, text="⏸ Show Full Path", 
                  command=lambda: self._draw_solution_board(canvas, self._parberry_solution),
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)
        
        tk.Button(btn_frame, text="Close", command=dlg.destroy,
                  bg="#2a2a3e", fg="#e8e0d0",
                  font=("Georgia", 11), relief="flat", bd=0,
                  padx=10, pady=6).pack(side="left", padx=4)

    # ── status helper  

    def _set_status(self, text, color="#78c8a0"):
        self._status_lbl.config(text=text, fg=color)

    
    #  LEADERBOARD
     

    def _show_leaderboard(self):
        self._clear()
        self.geometry(f"720x520+{self.center_x - 360}+{self.center_y - 260}")

        tk.Label(self, text="🏆  Leaderboard",
                 bg="#0f0f1a", fg="#f5c842",
                 font=("Georgia", 22, "bold")).pack(pady=(20, 4))
        tk.Label(self,
                 text="Players who completed a valid Knight's Tour",
                 bg="#0f0f1a", fg="#a09880",
                 font=("Georgia", 11)).pack(pady=(0, 12))

        frame = tk.Frame(self, bg="#0f0f1a")
        frame.pack(fill="both", expand=True, padx=24, pady=4)

        cols = ("Name", "Board", "Start", "Moves", "Sequence")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        tree.grid(row=0, column=0, sticky="nsew")

        sb_v = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        sb_v.grid(row=0, column=1, sticky="ns")
        
        sb_h = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        sb_h.grid(row=1, column=0, sticky="ew")
        
        tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        widths = [120, 70, 80, 60, 110]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")

        try:
            rows = fetch_winners()
            for row in rows:
                tree.insert("", "end", values=row)
        except RuntimeError as e:
            messagebox.showerror("DB Error", str(e))

        btn_f = tk.Frame(self, bg="#0f0f1a")
        btn_f.pack(pady=12)
        tk.Button(btn_f, text="☰  Main Menu",
                  command=self._show_menu,
                  bg="#2a2a3e", fg="#f5c842",
                  font=("Georgia", 12, "bold"), relief="flat", bd=0,
                  padx=14, pady=8).pack()

    
    #  TOURNAMENT SUMMARY
     

    def _show_tournament_summary(self):
        """Display a summary of all 20 rounds completed."""
        self._clear()
        self.geometry(f"700x700+{self.center_x - 350}+{self.center_y - 350}")

        tk.Label(self, text="📊  Tournament Summary",
                 bg="#0f0f1a", fg="#f5c842",
                 font=("Georgia", 22, "bold")).pack(pady=(20, 4))
        tk.Label(self,
                 text=f"All {self._total_rounds} rounds completed by {self._player_name}",
                 bg="#0f0f1a", fg="#a09880",
                 font=("Georgia", 11)).pack(pady=(0, 12))

        frame = tk.Frame(self, bg="#0f0f1a")
        frame.pack(fill="both", expand=True, padx=24, pady=4)

        # Create listbox to show round results
        sb = tk.Scrollbar(frame)
        sb.pack(side="right", fill="y")
        lb = tk.Listbox(frame, yscrollcommand=sb.set,
                        bg="#12121f", fg="#c8c0b0",
                        font=("Courier", 10),
                        highlightthickness=0, bd=0)
        lb.pack(fill="both", expand=True)
        sb.config(command=lb.yview)

        # Add round information
        total_moves = 0
        for score in self._round_scores:
            round_num = score['round']
            board_size = score['board_size']
            moves = score['moves']
            start = score['start']
            lb.insert("end", f"  Round {round_num:2d}:  {board_size}×{board_size} board  |  Start: {start}  |  Moves: {moves}")
            total_moves += moves

        # Add summary statistics
        lb.insert("end", "")
        lb.insert("end", "  " + "=" * 70)
        lb.insert("end", f"  Total Moves Across All Rounds: {total_moves}")
        lb.insert("end", f"  Average Moves Per Round: {total_moves / self._total_rounds:.1f}")
        lb.insert("end", "  " + "=" * 70)

        # Buttons
        btn_f = tk.Frame(self, bg="#0f0f1a")
        btn_f.pack(pady=12)
        tk.Button(btn_f, text="🏆  Save Tournament",
                  command=lambda: self._save_all_rounds_and_return(),
                  bg="#f5c842", fg="#0f0f1a",
                  font=("Georgia", 12, "bold"), relief="flat", bd=0,
                  padx=14, pady=8).pack(side="left", padx=4)
        tk.Button(btn_f, text="☰  Main Menu",
                  command=self._show_menu,
                  bg="#2a2a3e", fg="#f5c842",
                  font=("Georgia", 12, "bold"), relief="flat", bd=0,
                  padx=14, pady=8).pack(side="left", padx=4)

    def _save_all_rounds_and_return(self):
        """Save all rounds to database and return to menu."""
        messagebox.showinfo(
            "Tournament Completed",
            f"🏆 Congratulations {self._player_name}!\n\n"
            f"You completed all {self._total_rounds} rounds!\n"
            f"Total Rounds: {len(self._round_scores)}\n\n"
            f"All scores have been saved to the leaderboard."
        )
        self._show_menu()
