import tkinter as tk


# Professional color palette
THEME = {
    "bg": "#1a1a2e",  # Dark Navy
    "card_bg": "#16213e",  # Slightly lighter navy
    "accent": "#4cc9f0",  # Cyan
    "text": "#ffffff",  # White
    "win": "#90EE90",  # Light Green
    "lose": "#ff4d4d",  # Red
}

# Draw state (not in THEME keys)
DRAW_FG = "#fbbf24"
SECONDARY_TEXT = "#a2a2c2"


class ResultScreen:
    """Result screen showing win/lose message and game details."""

    def __init__(self, root, on_play_again, on_main_menu):
        """
        Initialize the result screen.

        Args:
            root: Tkinter root window
            on_play_again: Callback function for play again button
            on_main_menu: Callback function for main menu button
        """
        self.root = root
        self.on_play_again = on_play_again
        self.on_main_menu = on_main_menu

        self.frame = tk.Frame(root, bg=THEME["bg"], padx=50, pady=50)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.build_ui()

    def build_ui(self):
        """Build the result screen UI structure."""
        self.result_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 36, "bold"),
            bg=THEME["bg"],
            fg=THEME["text"],
        )
        self.result_label.pack(pady=(0, 30))

        details_frame = tk.LabelFrame(
            self.frame,
            text="Round Details",
            font=("Arial", 11, "bold"),
            fg=THEME["accent"],
            bg=THEME["card_bg"],
            padx=20,
            pady=20,
            highlightthickness=0,
            borderwidth=1,
            relief=tk.GROOVE,
        )
        details_frame.pack(fill=tk.X, pady=20)
        details_frame.configure(labelanchor="n")

        self.player_answer_label = tk.Label(
            details_frame,
            text="",
            font=("Arial", 14),
            bg=THEME["card_bg"],
            fg=THEME["text"],
        )
        self.player_answer_label.pack(pady=5)

        self.correct_answer_label = tk.Label(
            details_frame,
            text="",
            font=("Arial", 14),
            bg=THEME["card_bg"],
            fg=THEME["accent"],
        )
        self.correct_answer_label.pack(pady=5)

        self.algo_times_label = tk.Label(
            details_frame,
            text="",
            font=("Arial", 12),
            bg=THEME["card_bg"],
            fg=SECONDARY_TEXT,
        )
        self.algo_times_label.pack(pady=10)

        buttons_frame = tk.Frame(self.frame, bg=THEME["bg"])
        buttons_frame.pack(pady=30)

        play_again_button = tk.Button(
            buttons_frame,
            text="Play Again",
            command=self.on_play_again,
            font=("Arial", 14, "bold"),
            bg=THEME["accent"],
            fg=THEME["bg"],
            activebackground=THEME["text"],
            activeforeground=THEME["bg"],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
        )
        play_again_button.pack(side=tk.LEFT, padx=10)

        menu_button = tk.Button(
            buttons_frame,
            text="Back to Menu",
            command=self.on_main_menu,
            font=("Arial", 14),
            bg=THEME["card_bg"],
            fg=THEME["text"],
            activebackground=THEME["bg"],
            activeforeground=THEME["text"],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
        )
        menu_button.pack(side=tk.LEFT, padx=10)

    def show_result(self, game_result):
        """
        Display the game result.

        Args:
            game_result: Dictionary with round information
        """
        result = game_result["result"]
        player_answer = game_result["player_answer"]
        correct_answer = game_result["correct_max_flow"]
        algo1_time = game_result["algo1_time"]
        algo2_time = game_result["algo2_time"]

        if result == "Win":
            self.result_label.config(
                text="🎉 You Win!",
                fg=THEME["win"],
                bg=THEME["bg"],
            )
        elif result == "Lose":
            self.result_label.config(
                text="❌ You Lose!",
                fg=THEME["lose"],
                bg=THEME["bg"],
            )
        else:
            self.result_label.config(
                text="🤝 Draw!",
                fg=DRAW_FG,
                bg=THEME["bg"],
            )

        self.player_answer_label.config(text=f"Your Answer: {player_answer}")
        self.correct_answer_label.config(
            text=f"Correct Maximum Flow: {correct_answer}"
        )
        self.algo_times_label.config(
            text=f"Algorithm Times:\n"
            f"Ford-Fulkerson: {algo1_time:.8f} seconds\n"
            f"Edmonds-Karp: {algo2_time:.8f} seconds"
        )

    def destroy(self):
        """Destroy the result screen."""
        self.frame.destroy()
