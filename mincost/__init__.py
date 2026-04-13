# Minimum Cost Game - Tkinter UI
import tkinter as tk
from tkinter import ttk, messagebox
import random

from mincost.algorithms import run_round
from database.mincost import create_tables, save_round, get_all_rounds

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


class MinCostGame:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Minimum Cost - Task Assignment")
        self.window.geometry("980x720")
        self.window.resizable(False, False)
        self.window.configure(bg=BG_DARK)

        create_tables()
        self.round_number = 0
        self._has_played = False

        self._build_ui()

    # ========================================================
    #  Layout builder
    # ========================================================
    def _build_ui(self):
        # ---------- 1. Header ----------
        self._build_header()

        # ---------- 2. Controls ----------
        self._build_controls()

        # ---------- 3. Status bar (round / N / comparison) ----------
        self._build_status_bar()

        # ---------- 4. Main content area ----------
        self.content = tk.Frame(self.window, bg=BG_DARK)
        self.content.pack(fill=tk.BOTH, expand=True, padx=S6, pady=(S2, S4))

        # Empty state shown before first round
        self._build_empty_state()

        # Algorithm cards (hidden initially)
        self.cards_frame = tk.Frame(self.content, bg=BG_DARK)
        self.h_card = self._build_algo_card(
            self.cards_frame, "Hungarian Algorithm", "Optimal  |  Kuhn-Munkres  |  O(n\u00b3)", ACCENT_BLUE
        )
        self.h_card["frame"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, S2))

        self.g_card = self._build_algo_card(
            self.cards_frame, "Greedy Algorithm", "Heuristic  |  Sort & Pick  |  O(n\u00b2 log n)", ACCENT_ORANGE
        )
        self.g_card["frame"].pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(S2, 0))

        # ---------- 5. Footer ----------
        self._build_footer()

    # ---------- Header ----------
    def _build_header(self):
        bar = tk.Frame(self.window, bg=BG_SURFACE, height=56)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="MINIMUM COST", font=FONT_DISPLAY,
                 bg=BG_SURFACE, fg=ACCENT_BLUE).pack(side=tk.LEFT, padx=S6, pady=S3)

        tk.Label(bar, text="|", font=FONT_BODY,
                 bg=BG_SURFACE, fg=BORDER).pack(side=tk.LEFT, pady=S3)

        tk.Label(bar, text="  Task Assignment Optimizer", font=FONT_BODY,
                 bg=BG_SURFACE, fg=TEXT_SECONDARY).pack(side=tk.LEFT, pady=S3)

        # Back button - pill-shaped container with icon
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

        # Hover and click bindings for all child widgets
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
        tk.Frame(self.window, bg=ACCENT_BLUE, height=2).pack(fill=tk.X)

    # ---------- Controls ----------
    def _build_controls(self):
        row = tk.Frame(self.window, bg=BG_DARK)
        row.pack(fill=tk.X, padx=S6, pady=(S4, S2))

        # Input group
        input_grp = tk.Frame(row, bg=BG_DARK)
        input_grp.pack(side=tk.LEFT)

        tk.Label(input_grp, text="Tasks / Employees (N)", font=FONT_CAPTION_B,
                 bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor=tk.W)

        entry_row = tk.Frame(input_grp, bg=BG_DARK)
        entry_row.pack(anchor=tk.W, pady=(S1, 0))

        self.n_var = tk.StringVar()
        self.n_entry = tk.Entry(
            entry_row, textvariable=self.n_var, width=7, font=FONT_BODY,
            bg=BG_INPUT, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
            relief=tk.FLAT, highlightthickness=2, highlightcolor=ACCENT_BLUE,
            highlightbackground=BORDER, justify=tk.CENTER
        )
        self.n_entry.pack(side=tk.LEFT, ipady=5)
        self.n_entry.bind("<Return>", lambda e: self._play_round())

        tk.Label(entry_row, text="50 - 100", font=FONT_CAPTION,
                 bg=BG_DARK, fg=TEXT_MUTED).pack(side=tk.LEFT, padx=S2)

        # Action buttons
        btn_grp = tk.Frame(row, bg=BG_DARK)
        btn_grp.pack(side=tk.LEFT, padx=(S6, 0))

        # Vertical alignment spacer
        tk.Label(btn_grp, text="", font=FONT_CAPTION_B, bg=BG_DARK).pack(anchor=tk.W)

        btns_row = tk.Frame(btn_grp, bg=BG_DARK)
        btns_row.pack(anchor=tk.W, pady=(S1, 0))

        self._make_btn(btns_row, "Random N", ACCENT_PURPLE, TEXT_WHITE,
                       self._random_n).pack(side=tk.LEFT, padx=(0, S2))
        self._make_btn(btns_row, "Play Round", ACCENT_GREEN, BG_DARK,
                       self._play_round).pack(side=tk.LEFT)

        # Right-side history button
        right_grp = tk.Frame(row, bg=BG_DARK)
        right_grp.pack(side=tk.RIGHT)
        tk.Label(right_grp, text="", font=FONT_CAPTION_B, bg=BG_DARK).pack(anchor=tk.E)
        hist_row = tk.Frame(right_grp, bg=BG_DARK)
        hist_row.pack(anchor=tk.E, pady=(S1, 0))
        self._make_btn(hist_row, "View History", "#455a64", TEXT_PRIMARY,
                       self._show_history).pack()

    # ---------- Status bar ----------
    def _build_status_bar(self):
        bar = tk.Frame(self.window, bg=BG_DARK)
        bar.pack(fill=tk.X, padx=S6, pady=(S1, 0))

        self.lbl_round = self._make_badge(bar, "ROUND  --")
        self.lbl_round.pack(side=tk.LEFT, padx=(0, S2))

        self.lbl_n = self._make_badge(bar, "N  --")
        self.lbl_n.pack(side=tk.LEFT)

        self.lbl_compare = tk.Label(bar, text="", font=FONT_BODY_B,
                                    bg=BG_DARK, fg=TEXT_SECONDARY)
        self.lbl_compare.pack(side=tk.RIGHT)

    # ---------- Empty state ----------
    def _build_empty_state(self):
        self.empty_state = tk.Frame(self.content, bg=BG_SURFACE)
        self.empty_state.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(self.empty_state, bg=BG_SURFACE)
        inner.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        tk.Label(inner, text="No round played yet", font=FONT_H1,
                 bg=BG_SURFACE, fg=TEXT_SECONDARY).pack(pady=(0, S2))

        steps = [
            "1.  Enter N (50-100) or click Random N",
            "2.  Click Play Round to generate a cost matrix",
            "3.  Compare Hungarian vs Greedy results",
        ]
        for step in steps:
            tk.Label(inner, text=step, font=FONT_BODY,
                     bg=BG_SURFACE, fg=TEXT_MUTED).pack(anchor=tk.W, pady=2)

    # ---------- Footer ----------
    def _build_footer(self):
        ft = tk.Frame(self.window, bg=BG_DARK, height=28)
        ft.pack(fill=tk.X, side=tk.BOTTOM)
        ft.pack_propagate(False)
        tk.Label(ft, text="PDSA II  |  Minimum Cost Assignment Problem",
                 font=FONT_CAPTION, bg=BG_DARK, fg="#2a2a4a").pack(side=tk.LEFT, padx=S6)

    # ========================================================
    #  Reusable widget builders
    # ========================================================
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

    def _build_algo_card(self, parent, title, subtitle, accent):
        # Outer frame with colored border
        frame = tk.Frame(parent, bg=accent)
        inner = tk.Frame(frame, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)  # 1px border

        # ---- Card header ----
        hdr = tk.Frame(inner, bg=BG_CARD)
        hdr.pack(fill=tk.X, padx=S4, pady=(S4, 0))

        tk.Label(hdr, text=title, font=FONT_H2,
                 bg=BG_CARD, fg=accent).pack(anchor=tk.W)
        tk.Label(hdr, text=subtitle, font=FONT_CAPTION,
                 bg=BG_CARD, fg=TEXT_MUTED).pack(anchor=tk.W, pady=(2, 0))

        # Divider
        tk.Frame(inner, bg=BORDER, height=1).pack(fill=tk.X, padx=S4, pady=S3)

        # ---- Stats row ----
        stats = tk.Frame(inner, bg=BG_CARD)
        stats.pack(fill=tk.X, padx=S4)

        # Cost stat
        cost_box = tk.Frame(stats, bg=BG_CARD)
        cost_box.pack(side=tk.LEFT, expand=True)
        tk.Label(cost_box, text="TOTAL COST", font=FONT_CAPTION_B,
                 bg=BG_CARD, fg=TEXT_MUTED).pack()
        lbl_cost = tk.Label(cost_box, text="--", font=FONT_STAT,
                            bg=BG_CARD, fg=TEXT_WHITE)
        lbl_cost.pack()

        # Vertical separator
        tk.Frame(stats, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=S3, pady=S1)

        # Time stat
        time_box = tk.Frame(stats, bg=BG_CARD)
        time_box.pack(side=tk.RIGHT, expand=True)
        tk.Label(time_box, text="EXECUTION TIME", font=FONT_CAPTION_B,
                 bg=BG_CARD, fg=TEXT_MUTED).pack()
        lbl_time = tk.Label(time_box, text="--", font=FONT_STAT,
                            bg=BG_CARD, fg=accent)
        lbl_time.pack()

        # Divider
        tk.Frame(inner, bg=BORDER, height=1).pack(fill=tk.X, padx=S4, pady=(S3, S2))

        # ---- Assignment list header ----
        list_hdr = tk.Frame(inner, bg=BG_CARD)
        list_hdr.pack(fill=tk.X, padx=S4)
        tk.Label(list_hdr, text="EMPLOYEE", font=FONT_CAPTION_B,
                 bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)
        tk.Label(list_hdr, text="TASK", font=FONT_CAPTION_B,
                 bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT, padx=(S6, 0))
        tk.Label(list_hdr, text="COST", font=FONT_CAPTION_B,
                 bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.RIGHT)

        # ---- Assignment list ----
        list_wrap = tk.Frame(inner, bg=LISTBOX_BG, highlightbackground=BORDER,
                             highlightthickness=1)
        list_wrap.pack(fill=tk.BOTH, expand=True, padx=S4, pady=(S1, S4))

        scrollbar = tk.Scrollbar(list_wrap, troughcolor=BG_DARK, bg=BG_INPUT,
                                 activebackground=ACCENT_BLUE, relief=tk.FLAT,
                                 borderwidth=0)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(
            list_wrap, yscrollcommand=scrollbar.set, font=FONT_MONO,
            bg=LISTBOX_BG, fg=TEXT_SECONDARY, selectbackground=BG_INPUT,
            selectforeground=TEXT_WHITE, relief=tk.FLAT, borderwidth=0,
            highlightthickness=0, activestyle="none"
        )
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        return {
            "frame": frame,
            "lbl_cost": lbl_cost,
            "lbl_time": lbl_time,
            "listbox": listbox,
        }

    # ========================================================
    #  Actions
    # ========================================================
    def _random_n(self):
        self.n_var.set(str(random.randint(50, 100)))
        self.n_entry.focus_set()

    def _play_round(self):
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

        # --- Swap empty state for cards on first play ---
        if not self._has_played:
            self.empty_state.pack_forget()
            self.cards_frame.pack(fill=tk.BOTH, expand=True)
            self._has_played = True

        # --- Run algorithms ---
        self.round_number += 1
        results = run_round(n)
        h = results["hungarian"]
        g = results["greedy"]

        # Persist
        save_round(self.round_number, n, h["cost"], h["time_ms"], g["cost"], g["time_ms"])

        # --- Update status badges ---
        self.lbl_round.config(text=f"ROUND  {self.round_number:02d}")
        self.lbl_n.config(text=f"N  {n}")

        # --- Update cards ---
        self.h_card["lbl_cost"].config(text=f"${h['cost']:,}")
        self.h_card["lbl_time"].config(text=f"{h['time_ms']} ms")

        self.g_card["lbl_cost"].config(text=f"${g['cost']:,}")
        self.g_card["lbl_time"].config(text=f"{g['time_ms']} ms")

        # --- Fill assignment lists ---
        for card, key in [(self.h_card, "hungarian"), (self.g_card, "greedy")]:
            card["listbox"].delete(0, tk.END)
            for emp in range(n):
                task = results[key]["assignment"][emp]
                cost = results["cost_matrix"][emp][task]
                card["listbox"].insert(
                    tk.END,
                    f"  Emp {emp+1:>3}    ->    Task {task+1:>3}        ${cost:>3}"
                )

        # --- Comparison ---
        diff = g["cost"] - h["cost"]
        if diff > 0:
            pct = (diff / h["cost"]) * 100
            self.lbl_compare.config(
                text=f"Greedy is ${diff:,} more expensive  (+{pct:.1f}%)",
                fg=ACCENT_RED
            )
        else:
            self.lbl_compare.config(
                text="Both algorithms found the same optimal cost",
                fg=ACCENT_GREEN
            )

        # Pre-fill next random N
        self.n_var.set(str(random.randint(50, 100)))

    def _show_history(self):
        rows = get_all_rounds()

        win = tk.Toplevel(self.window)
        win.title("Game History")
        win.geometry("880x480")
        win.resizable(False, True)
        win.configure(bg=BG_DARK)

        # Header
        hdr = tk.Frame(win, bg=BG_SURFACE, height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="GAME HISTORY", font=FONT_H1,
                 bg=BG_SURFACE, fg=ACCENT_BLUE).pack(side=tk.LEFT, padx=S6, pady=S3)
        tk.Label(hdr, text=f"{len(rows)} rounds recorded", font=FONT_CAPTION,
                 bg=BG_SURFACE, fg=TEXT_MUTED).pack(side=tk.LEFT, padx=S2, pady=S3)
        tk.Frame(win, bg=ACCENT_BLUE, height=2).pack(fill=tk.X)

        if not rows:
            tk.Label(win, text="No rounds played yet. Play a round first!",
                     font=FONT_BODY, bg=BG_DARK, fg=TEXT_MUTED).pack(expand=True)
            return

        # Styled treeview
        style = ttk.Style(win)
        style.theme_use("clam")
        style.configure("H.Treeview",
                        background=BG_CARD, foreground=TEXT_PRIMARY,
                        fieldbackground=BG_CARD, font=FONT_CAPTION,
                        rowheight=30, borderwidth=0)
        style.configure("H.Treeview.Heading",
                        background=BG_INPUT, foreground=ACCENT_BLUE,
                        font=FONT_CAPTION_B, relief=tk.FLAT, borderwidth=0)
        style.map("H.Treeview",
                  background=[("selected", BG_HOVER)],
                  foreground=[("selected", TEXT_WHITE)])
        style.layout("H.Treeview", [("H.Treeview.treearea", {"sticky": "nswe"})])

        columns = ("Round", "N", "Hungarian $", "Hungarian ms",
                   "Greedy $", "Greedy ms", "Date")
        tree = ttk.Treeview(win, columns=columns, show="headings",
                            height=15, style="H.Treeview")

        widths = [65, 50, 115, 115, 110, 110, 170]
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor=tk.CENTER, minwidth=w)

        vsb = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        for r in rows:
            tree.insert("", tk.END, values=(
                r[0], r[1],
                f"${r[2]:,.0f}", f"{r[3]:.2f}",
                f"${r[4]:,.0f}", f"{r[5]:.2f}",
                r[6] or ""
            ))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(S4, 0), pady=S4)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, S4), pady=S4)


def open_mincost_game(parent):
    MinCostGame(parent)
