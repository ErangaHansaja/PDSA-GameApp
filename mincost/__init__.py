# Minimum Cost Game - Tkinter UI
import tkinter as tk
from tkinter import ttk, messagebox
import random
import uuid

from mincost.algorithms import run_round, generate_choices
from database.mincost import create_tables, save_round, update_overall_result, get_all_rounds

# ============================================================
#  Design Tokens  (8px spacing scale, consistent palette)
# ============================================================
BG_DARK = "#0f0f1a"
BG_SURFACE = "#1a1a2e"
BG_CARD = "#16213e"
BG_INPUT = "#0f3460"
BG_HOVER = "#1e2a4a"
LISTBOX_BG = "#0d1b2a"

ACCENT_BLUE = "#4fc3f7"
ACCENT_GREEN = "#66bb6a"
ACCENT_ORANGE = "#ffa726"
ACCENT_RED = "#ef5350"
ACCENT_PURPLE = "#b388ff"

TEXT_PRIMARY = "#e8eaf6"
TEXT_SECONDARY = "#90a4ae"
TEXT_MUTED = "#546e7a"
TEXT_WHITE = "#ffffff"
BORDER = "#2a3a5c"

# Spacing scale (multiples of 8)
S1 = 4
S2 = 8
S3 = 12
S4 = 16
S5 = 20
S6 = 24

# Typography scale
FONT_DISPLAY = ("Segoe UI", 20, "bold")
FONT_H1 = ("Segoe UI", 14, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_BODY_B = ("Segoe UI", 11, "bold")
FONT_CAPTION = ("Segoe UI", 9)
FONT_CAPTION_B = ("Segoe UI", 9, "bold")
FONT_STAT = ("Segoe UI", 18, "bold")
FONT_STAT_UNIT = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 9)
FONT_BTN = ("Segoe UI", 10, "bold")

TOTAL_ROUNDS = 20


class MinCostGame:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Minimum Cost - Task Assignment")
        self.window.geometry("1100x800")
        self.window.resizable(False, False)
        self.window.configure(bg=BG_DARK)

        create_tables()

        # Game state
        self.game_id = str(uuid.uuid4())
        self.player_name = ""
        self.round_number = 0
        self.wins = 0
        self.losses = 0
        self.round_data = []
        self.current_result = None
        self.correct_answer = 0
        self.choice_buttons = []

        self._build_name_screen()

    #  Screen 1: Player name entry
    def _build_name_screen(self):
        self.name_frame = tk.Frame(self.window, bg=BG_DARK)
        self.name_frame.pack(fill=tk.BOTH, expand=True)

        center = tk.Frame(self.name_frame, bg=BG_SURFACE, padx=48, pady=40)
        center.place(relx=0.5, rely=0.42, anchor=tk.CENTER)

        tk.Label(center, text="MINIMUM COST GAME", font=FONT_DISPLAY,
                 bg=BG_SURFACE, fg=ACCENT_BLUE).pack(pady=(0, S3))

        tk.Label(center, text="Task Assignment Challenge  \u2022  20 Rounds",
                 font=FONT_BODY, bg=BG_SURFACE, fg=TEXT_SECONDARY).pack(pady=(0, S6))

        tk.Frame(center, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, S5))

        tk.Label(center, text="Enter your name", font=FONT_H2,
                 bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor=tk.W, pady=(0, S2))

        self.name_entry = tk.Entry(
            center, font=FONT_BODY, width=28,
            bg=BG_INPUT, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
            relief=tk.FLAT, highlightthickness=2,
            highlightcolor=ACCENT_BLUE, highlightbackground=BORDER
        )
        self.name_entry.pack(ipady=6, pady=(0, S5))
        self.name_entry.focus_set()
        self.name_entry.bind("<Return>", lambda e: self._start_game())

        self._make_btn(center, "  Start Game  ", ACCENT_GREEN, BG_DARK,
                       self._start_game).pack(ipadx=S5, ipady=S1)

    def _start_game(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Name Required",
                                   "Please enter your name to start the game.")
            self.name_entry.focus_set()
            return

        self.player_name = name
        self.name_frame.pack_forget()
        self._build_game_screen()
        self._setup_round()

    #  Screen 2: Game rounds
    def _build_game_screen(self):
        self.game_frame = tk.Frame(self.window, bg=BG_DARK)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        # ---------- Header ----------
        bar = tk.Frame(self.game_frame, bg=BG_SURFACE, height=56)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="MINIMUM COST", font=FONT_DISPLAY,
                 bg=BG_SURFACE, fg=ACCENT_BLUE).pack(side=tk.LEFT, padx=S6, pady=S3)

        tk.Label(bar, text="|", font=FONT_BODY,
                 bg=BG_SURFACE, fg=BORDER).pack(side=tk.LEFT, pady=S3)

        tk.Label(bar, text=f"  Player: {self.player_name}", font=FONT_BODY,
                 bg=BG_SURFACE, fg=TEXT_SECONDARY).pack(side=tk.LEFT, pady=S3)

        # Back button - same style as original
        back_wrap = tk.Frame(bar, bg="#2a3a5c", padx=1, pady=1)
        back_wrap.pack(side=tk.RIGHT, padx=S6, pady=10)

        back_inner = tk.Frame(back_wrap, bg=BG_INPUT, cursor="hand2")
        back_inner.pack()

        back_arrow = tk.Label(
            back_inner, text="\u2190", font=("Segoe UI", 12),
            bg=BG_INPUT, fg=ACCENT_BLUE, cursor="hand2"
        )
        back_arrow.pack(side=tk.LEFT, padx=(S3, 2), pady=S1)

        back_text = tk.Label(
            back_inner, text="Dashboard", font=FONT_CAPTION_B,
            bg=BG_INPUT, fg=TEXT_PRIMARY, cursor="hand2"
        )
        back_text.pack(side=tk.LEFT, padx=(0, S3), pady=S1)

        hover_targets = [back_wrap, back_inner, back_arrow, back_text]
        for w in hover_targets:
            w.bind("<Enter>", lambda e: [
                back_inner.config(bg=ACCENT_BLUE),
                back_arrow.config(bg=ACCENT_BLUE, fg=BG_DARK),
                back_text.config(bg=ACCENT_BLUE, fg=BG_DARK),
                back_wrap.config(bg=ACCENT_BLUE),
            ])
            w.bind("<Leave>", lambda e: [
                back_inner.config(bg=BG_INPUT),
                back_arrow.config(bg=BG_INPUT, fg=ACCENT_BLUE),
                back_text.config(bg=BG_INPUT, fg=TEXT_PRIMARY),
                back_wrap.config(bg="#2a3a5c"),
            ])
            w.bind("<Button-1>", lambda e: self.window.destroy())

        # Accent line
        tk.Frame(self.game_frame, bg=ACCENT_BLUE, height=2).pack(fill=tk.X)

        # Status bar
        status = tk.Frame(self.game_frame, bg=BG_DARK)
        status.pack(fill=tk.X, padx=S6, pady=(S3, 0))

        self.lbl_round = self._make_badge(status, "ROUND  01 / 20")
        self.lbl_round.pack(side=tk.LEFT, padx=(0, S2))

        self.lbl_n = self._make_badge(status, "N  --")
        self.lbl_n.pack(side=tk.LEFT)

        self.lbl_score = tk.Label(
            status, text="Score:  0W - 0L", font=FONT_BODY_B,
            bg=BG_DARK, fg=TEXT_SECONDARY
        )
        self.lbl_score.pack(side=tk.RIGHT)

        # Content area
        self.content = tk.Frame(self.game_frame, bg=BG_DARK)
        self.content.pack(fill=tk.BOTH, expand=True, padx=S6, pady=S2)

    def _setup_round(self):
        """Clear content and prepare for a new round."""
        for w in self.content.winfo_children():
            w.destroy()

        self.round_number += 1
        self.lbl_round.config(text=f"ROUND  {self.round_number:02d} / {TOTAL_ROUNDS}")
        self.lbl_n.config(text="N  --")

        # Controls row
        ctrl = tk.Frame(self.content, bg=BG_DARK)
        ctrl.pack(fill=tk.X, pady=(S2, S3))

        input_grp = tk.Frame(ctrl, bg=BG_DARK)
        input_grp.pack(side=tk.LEFT)

        tk.Label(input_grp, text="Tasks / Employees (N)", font=FONT_CAPTION_B,
                 bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor=tk.W)

        entry_row = tk.Frame(input_grp, bg=BG_DARK)
        entry_row.pack(anchor=tk.W, pady=(S1, 0))

        self.n_var = tk.StringVar(value=str(random.randint(50, 100)))
        self.n_entry = tk.Entry(
            entry_row, textvariable=self.n_var, width=7, font=FONT_BODY,
            bg=BG_INPUT, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
            relief=tk.FLAT, highlightthickness=2, highlightcolor=ACCENT_BLUE,
            highlightbackground=BORDER, justify=tk.CENTER
        )
        self.n_entry.pack(side=tk.LEFT, ipady=5)
        self.n_entry.bind("<Return>", lambda e: self._generate_round())
        self.n_entry.focus_set()

        tk.Label(entry_row, text="50 - 100", font=FONT_CAPTION,
                 bg=BG_DARK, fg=TEXT_MUTED).pack(side=tk.LEFT, padx=S2)

        # Action buttons
        btn_grp = tk.Frame(ctrl, bg=BG_DARK)
        btn_grp.pack(side=tk.LEFT, padx=(S6, 0))

        # Vertical alignment spacer
        tk.Label(btn_grp, text="", font=FONT_CAPTION_B, bg=BG_DARK).pack(anchor=tk.W)

        btns_row = tk.Frame(btn_grp, bg=BG_DARK)
        btns_row.pack(anchor=tk.W, pady=(S1, 0))

        self._make_btn(btns_row, "Random N", ACCENT_PURPLE, TEXT_WHITE,
                       self._random_n).pack(side=tk.LEFT, padx=(0, S2))
        self.gen_btn = self._make_btn(btns_row, "Generate", ACCENT_GREEN, BG_DARK,
                                      self._generate_round)
        self.gen_btn.pack(side=tk.LEFT)

        # Instruction text
        self.instruction = tk.Label(
            self.content,
            text="Enter N (50\u2013100) or click Random N, then click Generate",
            font=FONT_BODY, bg=BG_DARK, fg=TEXT_MUTED
        )
        self.instruction.pack(expand=True)

    # Round actions
    def _random_n(self):
        self.n_var.set(str(random.randint(50, 100)))
        self.n_entry.focus_set()

    def _generate_round(self):
        # --- Input validation ---
        raw = self.n_var.get().strip()
        if not raw:
            messagebox.showwarning("Input Required",
                                   "Please enter a value for N or click Random N.")
            self.n_entry.focus_set()
            return
        try:
            n = int(raw)
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "N must be a whole number between 50 and 100.")
            self.n_entry.focus_set()
            return
        if n < 50 or n > 100:
            messagebox.showerror("Out of Range",
                                 "N must be between 50 and 100.")
            self.n_entry.focus_set()
            return

        # Disable controls while processing
        self.n_entry.config(state=tk.DISABLED)
        self.gen_btn.config(state=tk.DISABLED)
        self.instruction.pack_forget()

        # Run both algorithms
        self.current_result = run_round(n)
        self.lbl_n.config(text=f"N  {n}")

        # Generate answer choices
        correct = self.current_result["hungarian"]["cost"]
        self.correct_answer = correct
        self.choices = generate_choices(correct)

        # Display the cost matrix
        self._show_matrix()

        # Show multiple-choice answers
        self._show_choices()

    def _show_matrix(self):
        cm = self.current_result["cost_matrix"]
        n = self.current_result["n"]

        tk.Label(self.content, text="Cost Matrix (Employee \u00d7 Task)",
                 font=FONT_CAPTION_B, bg=BG_DARK, fg=TEXT_SECONDARY
                 ).pack(anchor=tk.W, pady=(0, S1))

        # Bordered wrapper
        text_wrap = tk.Frame(self.content, bg=BORDER)
        text_wrap.pack(fill=tk.X, pady=(0, S3))

        inner = tk.Frame(text_wrap, bg=BG_DARK)
        inner.pack(fill=tk.X, padx=1, pady=1)

        xsb = tk.Scrollbar(inner, orient=tk.HORIZONTAL)
        ysb = tk.Scrollbar(inner, orient=tk.VERTICAL)

        txt = tk.Text(
            inner, wrap=tk.NONE, font=FONT_MONO,
            bg=LISTBOX_BG, fg=TEXT_SECONDARY,
            xscrollcommand=xsb.set, yscrollcommand=ysb.set,
            relief=tk.FLAT, highlightthickness=0,
            padx=4, pady=4, height=10
        )

        xsb.config(command=txt.xview)
        ysb.config(command=txt.yview)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        xsb.pack(side=tk.BOTTOM, fill=tk.X)
        txt.pack(fill=tk.X)

        # Header row (task numbers)
        header = "      " + "".join(f"{j+1:>5}" for j in range(n))
        txt.insert(tk.END, header + "\n")

        # Data rows (employee -> costs)
        for i in range(n):
            row = f"{i+1:>4}  " + "".join(f"{cm[i][j]:>5}" for j in range(n))
            txt.insert(tk.END, row + "\n")

        txt.config(state=tk.DISABLED)

    def _show_choices(self):
        choice_frame = tk.Frame(self.content, bg=BG_DARK)
        choice_frame.pack(fill=tk.X, pady=(S1, S2))

        tk.Label(choice_frame, text="What is the minimum total assignment cost?",
                 font=FONT_H2, bg=BG_DARK, fg=TEXT_PRIMARY
                 ).pack(anchor=tk.W, pady=(0, S3))

        btn_row = tk.Frame(choice_frame, bg=BG_DARK)
        btn_row.pack(anchor=tk.W)

        labels = ["A", "B", "C"]
        self.choice_buttons = []
        for i, val in enumerate(self.choices):
            btn = self._make_btn(
                btn_row, f"  {labels[i]})  ${val:,}  ",
                BG_INPUT, TEXT_WHITE,
                lambda v=val: self._pick_answer(v)
            )
            btn.pack(side=tk.LEFT, padx=(0, S3), ipady=4)
            btn._choice_val = val
            self.choice_buttons.append(btn)

    def _pick_answer(self, guess):
        h = self.current_result["hungarian"]
        g = self.current_result["greedy"]
        n = self.current_result["n"]

        is_correct = (guess == self.correct_answer)
        round_result = "CORRECT" if is_correct else "WRONG"

        if is_correct:
            self.wins += 1
        else:
            self.losses += 1

        self.lbl_score.config(text=f"Score:  {self.wins}W - {self.losses}L")

        # Highlight correct / wrong buttons
        for btn in self.choice_buttons:
            btn.config(state=tk.DISABLED)
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")
            if btn._choice_val == self.correct_answer:
                btn.config(bg=ACCENT_GREEN, fg=BG_DARK)
            elif btn._choice_val == guess and not is_correct:
                btn.config(bg=ACCENT_RED, fg=TEXT_WHITE)

        # Save round to database
        save_round(
            self.game_id, self.player_name, self.round_number, n,
            float(guess), float(self.correct_answer),
            float(h["cost"]), h["time_ms"],
            float(g["cost"]), g["time_ms"],
            round_result
        )

        # Keep data for end-game summary
        self.round_data.append({
            "round": self.round_number, "n": n,
            "guess": guess, "correct": self.correct_answer,
            "h_cost": h["cost"], "h_time": h["time_ms"],
            "g_cost": g["cost"], "g_time": g["time_ms"],
            "result": round_result,
        })

        # Show result panel below
        self._show_round_result(is_correct, guess)

    def _show_round_result(self, is_correct, guess):
        h = self.current_result["hungarian"]
        g = self.current_result["greedy"]

        res = tk.Frame(self.content, bg=BG_DARK)
        res.pack(fill=tk.X, pady=(S2, 0))

        # Result banner
        color = ACCENT_GREEN if is_correct else ACCENT_RED
        icon = "\u2713" if is_correct else "\u2717"
        msg = "Correct!" if is_correct else f"Wrong! You picked ${guess:,}"

        banner = tk.Frame(res, bg=color)
        banner.pack(fill=tk.X, pady=(0, S2))
        banner_in = tk.Frame(banner, bg=BG_CARD)
        banner_in.pack(fill=tk.X, padx=2, pady=2)
        tk.Label(banner_in, text=f"  {icon}  {msg}", font=FONT_H2,
                 bg=BG_CARD, fg=color, anchor=tk.W
                 ).pack(fill=tk.X, padx=S3, pady=S2)

        if not is_correct:
            tk.Label(res, text=f"Correct answer: ${self.correct_answer:,}",
                     font=FONT_BODY_B, bg=BG_DARK, fg=TEXT_PRIMARY
                     ).pack(anchor=tk.W, pady=(0, S2))

        # Algorithm comparison stats
        stats = tk.Frame(res, bg=BG_SURFACE)
        stats.pack(fill=tk.X, pady=(0, S2))

        for label, data, accent in [("Hungarian (Optimal)", h, ACCENT_BLUE),
                                     ("Greedy (Heuristic)", g, ACCENT_ORANGE)]:
            box = tk.Frame(stats, bg=BG_SURFACE)
            box.pack(side=tk.LEFT, expand=True, padx=S4, pady=S3)
            tk.Label(box, text=label, font=FONT_CAPTION_B,
                     bg=BG_SURFACE, fg=accent).pack()
            tk.Label(box, text=f"${data['cost']:,}", font=FONT_STAT,
                     bg=BG_SURFACE, fg=TEXT_WHITE).pack()
            tk.Label(box, text=f"{data['time_ms']} ms", font=FONT_CAPTION,
                     bg=BG_SURFACE, fg=accent).pack()

        # Cost comparison text
        diff = g["cost"] - h["cost"]
        if diff > 0:
            pct = (diff / h["cost"]) * 100
            cmp_text = f"Greedy is ${diff:,} more expensive  (+{pct:.1f}%)"
            cmp_color = ACCENT_RED
        else:
            cmp_text = "Both algorithms found the same cost"
            cmp_color = ACCENT_GREEN

        tk.Label(res, text=cmp_text, font=FONT_BODY_B,
                 bg=BG_DARK, fg=cmp_color).pack(pady=(0, S3))

        # Next round / View results button
        if self.round_number < TOTAL_ROUNDS:
            self._make_btn(res, "  Next Round  \u2192  ", ACCENT_BLUE, BG_DARK,
                           self._next_round).pack(anchor=tk.CENTER, ipadx=S5, ipady=S1)
        else:
            self._make_btn(res, "  View Results  \u2192  ", ACCENT_GREEN, BG_DARK,
                           self._show_summary).pack(anchor=tk.CENTER, ipadx=S5, ipady=S1)

    def _next_round(self):
        self._setup_round()

    # Screen 3: End game summary
    def _show_summary(self):
        # Determine overall result and update DB
        overall = "WIN" if self.wins > self.losses else "LOSE"
        update_overall_result(self.game_id, overall)

        self.game_frame.pack_forget()

        summ = tk.Frame(self.window, bg=BG_DARK)
        summ.pack(fill=tk.BOTH, expand=True)

        # Header
        hdr = tk.Frame(summ, bg=BG_SURFACE, height=56)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="GAME OVER", font=FONT_DISPLAY,
                 bg=BG_SURFACE, fg=ACCENT_BLUE).pack(side=tk.LEFT, padx=S6, pady=S3)
        tk.Frame(summ, bg=ACCENT_BLUE, height=2).pack(fill=tk.X)

        # Win or lose
        if self.wins > self.losses:
            res_text, res_color = "You Won!", ACCENT_GREEN
        else:
            res_text, res_color = "You Lost!", ACCENT_RED

        tk.Label(summ, text=res_text, font=("Segoe UI", 28, "bold"),
                 bg=BG_DARK, fg=res_color).pack(pady=(S6, S2))

        ratio = (self.wins / TOTAL_ROUNDS) * 100
        tk.Label(summ,
                 text=f"{self.wins} Wins  |  {self.losses} Losses  |  {ratio:.0f}% Win Rate",
                 font=FONT_H1, bg=BG_DARK, fg=TEXT_PRIMARY).pack(pady=(0, S2))

        tk.Label(summ, text=f"Player: {self.player_name}",
                 font=FONT_BODY, bg=BG_DARK, fg=TEXT_SECONDARY).pack(pady=(0, S4))

        # Round details table
        tk.Label(summ, text="Round Details", font=FONT_H2,
                 bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor=tk.W, padx=S6)

        table_wrap = tk.Frame(summ, bg=BG_DARK)
        table_wrap.pack(fill=tk.BOTH, expand=True, padx=S6, pady=(S2, 0))

        style = ttk.Style(summ)
        style.theme_use("clam")
        style.configure("S.Treeview",
                        background=BG_CARD, foreground=TEXT_PRIMARY,
                        fieldbackground=BG_CARD, font=FONT_CAPTION,
                        rowheight=26, borderwidth=0)
        style.configure("S.Treeview.Heading",
                        background=BG_INPUT, foreground=ACCENT_BLUE,
                        font=FONT_CAPTION_B, relief=tk.FLAT, borderwidth=0)
        style.map("S.Treeview",
                  background=[("selected", BG_HOVER)],
                  foreground=[("selected", TEXT_WHITE)])
        style.layout("S.Treeview", [("S.Treeview.treearea", {"sticky": "nswe"})])

        cols = ("Round", "N", "Your Guess", "Correct Ans", "Result",
                "Hungarian $", "H Time", "Greedy $", "G Time")
        tree = ttk.Treeview(table_wrap, columns=cols, show="headings",
                            height=12, style="S.Treeview")

        widths = [55, 45, 100, 100, 70, 100, 85, 100, 85]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor=tk.CENTER, minwidth=w)

        vsb = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        for rd in self.round_data:
            tree.insert("", tk.END, values=(
                rd["round"], rd["n"],
                f"${rd['guess']:,}", f"${rd['correct']:,}",
                rd["result"],
                f"${rd['h_cost']:,}", f"{rd['h_time']:.2f} ms",
                f"${rd['g_cost']:,}", f"{rd['g_time']:.2f} ms",
            ))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Back to dashboard
        self._make_btn(summ, "  Back to Dashboard  ", "#455a64", TEXT_PRIMARY,
                       self.window.destroy).pack(pady=S4)

    # Reusable widget builders
    def _make_btn(self, parent, text, bg, fg, command):
        btn = tk.Button(
            parent, text=text, font=FONT_BTN,
            bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
            relief=tk.FLAT, cursor="hand2", padx=S4, pady=S1,
            command=command, borderwidth=0
        )
        # Hover feedback
        lighter = self._lighten(bg, 25)
        btn.bind("<Enter>", lambda e: btn.config(bg=lighter))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    @staticmethod
    def _lighten(hex_color, amount):
        hex_color = hex_color.lstrip("#")
        r = min(255, int(hex_color[0:2], 16) + amount)
        g = min(255, int(hex_color[2:4], 16) + amount)
        b = min(255, int(hex_color[4:6], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _make_badge(self, parent, text):
        return tk.Label(
            parent, text=text, font=FONT_CAPTION_B,
            bg=BG_INPUT, fg=ACCENT_BLUE, padx=S3, pady=S1
        )


def open_mincost_game(parent):
    MinCostGame(parent)
