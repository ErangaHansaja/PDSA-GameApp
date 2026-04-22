# Launches the dashboard UI - main entry point
import tkinter as tk
from tkinter import messagebox

from mincost import open_mincost_game
from queens import open_queens_game
from snakeladder import open_snake_ladder

# --- Shared Design Tokens ---
BG_DARK = "#0f0f1a"
BG_SURFACE = "#1a1a2e"
BG_CARD = "#16213e"
ACCENT = "#4fc3f7"
TEXT_PRIMARY = "#e8eaf6"
TEXT_MUTED = "#7986cb"
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SUB = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 12, "bold")
FONT_DESC = ("Segoe UI", 9)


def show_coming_soon(game_name):
    messagebox.showinfo(game_name, "Coming Soon")


def open_traffic_game(root):
    """Launch Traffic Simulation - destroys dashboard, reopens on exit."""
    root.destroy()

    import sys, os
    traffic_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "traffic")
    if traffic_dir not in sys.path:
        sys.path.insert(0, traffic_dir)

    from traffic.main import MaximumFlowGame
    app = MaximumFlowGame()

    def go_back():
        app.root.destroy()
        main()

    app.handle_back_to_dashboard = go_back
    app.run()


def _on_enter(e, btn, color):
    btn.config(bg=color)


def _on_leave(e, btn, color):
    btn.config(bg=color)


def main():
    root = tk.Tk()
    root.title("PDSA Game Suite")
    root.geometry("480x550")
    root.resizable(False, False)
    root.configure(bg=BG_DARK)

    # Header
    header = tk.Frame(root, bg=BG_SURFACE, height=80)
    header.pack(fill=tk.X)
    header.pack_propagate(False)

    tk.Label(
        header, text="PDSA GAME SUITE", font=FONT_TITLE,
        bg=BG_SURFACE, fg=ACCENT
    ).pack(side=tk.LEFT, padx=24, pady=20)

    tk.Label(
        header, text="v1.0", font=FONT_SUB,
        bg=BG_SURFACE, fg=TEXT_MUTED
    ).pack(side=tk.LEFT, pady=20)

    tk.Frame(root, bg=ACCENT, height=2).pack(fill=tk.X)

    # Subtitle
    tk.Label(
        root, text="Select a game to begin", font=FONT_SUB,
        bg=BG_DARK, fg=TEXT_MUTED
    ).pack(pady=(20, 12))

    # Game Buttons
    games = [
        ("Minimum Cost", "Optimal task-to-employee assignment", "#00c853", lambda: open_mincost_game(root)),
        ("Snake and Ladder", "Classic board game simulation", "#7c4dff", lambda: open_snake_ladder(root)),
        ("Traffic Simulation", "Network flow optimization", "#ff6d00", lambda: open_traffic_game(root)),
        ("Knight's Tour", "Chessboard traversal challenge", "#e91e63", lambda: show_coming_soon("Knight's Tour")),
        ("Sixteen Queens", "N-Queens placement puzzle", "#fdd835", lambda: open_queens_game(root)),
    ]

    for name, desc, color, cmd in games:
        card = tk.Frame(root, bg=BG_CARD, cursor="hand2")
        card.pack(fill=tk.X, padx=28, pady=4, ipady=6)

        # Color indicator strip on the left
        strip = tk.Frame(card, bg=color, width=4)
        strip.pack(side=tk.LEFT, fill=tk.Y)

        text_area = tk.Frame(card, bg=BG_CARD)
        text_area.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=16, pady=6)

        tk.Label(
            text_area, text=name, font=FONT_BTN,
            bg=BG_CARD, fg=TEXT_PRIMARY, anchor=tk.W
        ).pack(anchor=tk.W)

        tk.Label(
            text_area, text=desc, font=FONT_DESC,
            bg=BG_CARD, fg=TEXT_MUTED, anchor=tk.W
        ).pack(anchor=tk.W)

        arrow = tk.Label(card, text=">", font=FONT_BTN, bg=BG_CARD, fg=TEXT_MUTED)
        arrow.pack(side=tk.RIGHT, padx=16)

        # Hover feedback - all widgets in the card
        hover_bg = "#1e2a4a"
        widgets = [card, text_area, arrow] + list(text_area.winfo_children())
        for w in widgets:
            w.bind("<Enter>", lambda e, c=card, ws=widgets, hb=hover_bg: [x.config(bg=hb) for x in ws])
            w.bind("<Leave>", lambda e, c=card, ws=widgets: [x.config(bg=BG_CARD) for x in ws])
            w.bind("<Button-1>", lambda e, fn=cmd: fn())

    # Footer
    tk.Label(
        root, text="PDSA II - Algorithm Visualizer", font=("Segoe UI", 8),
        bg=BG_DARK, fg="#3a3a5c"
    ).pack(side=tk.BOTTOM, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
