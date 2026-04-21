import tkinter as tk


# Consistent professional color palette
THEME = {
    "bg": "#1a1a2e",
    "card_bg": "#16213e",
    "accent": "#4cc9f0",
    "text": "#ffffff",
    "secondary_text": "#a2a2c2",
}

ERROR_FG = "#f87171"


class StartScreen:
    """Start screen for the Maximum Flow Game."""

    def __init__(self, root, on_start, on_statistics=None, on_back_to_dashboard=None):
        """
        Initialize the start screen.

        Args:
            root: Tkinter root window
            on_start: Callback function when game starts (receives player_name)
            on_statistics: Optional callback for opening statistics screen
            on_back_to_dashboard: Optional callback when Back to Dashboard is clicked
        """
        self.root = root
        self.on_start = on_start
        self.on_statistics = on_statistics
        self.on_back_to_dashboard = on_back_to_dashboard

        self.frame = tk.Frame(root, bg=THEME["bg"], padx=50, pady=50)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.build_ui()

    def build_ui(self):
        """Build the start screen UI."""
        title_label = tk.Label(
            self.frame,
            text="Traffic Simulation Problem",
            font=("Arial", 32, "bold"),
            bg=THEME["bg"],
            fg=THEME["text"],
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(
            self.frame,
            text="Maximum Flow in Traffic Networks",
            font=("Arial", 14),
            bg=THEME["bg"],
            fg=THEME["secondary_text"],
        )
        subtitle_label.pack(pady=(0, 20))

        desc_label = tk.Label(
            self.frame,
            text="Find the maximum vehicle flow from source A to sink T\n"
            "in a traffic network with random road capacities.",
            font=("Arial", 14),
            bg=THEME["bg"],
            fg=THEME["secondary_text"],
            justify=tk.CENTER,
        )
        desc_label.pack(pady=(0, 40))

        name_frame = tk.Frame(self.frame, bg=THEME["bg"])
        name_frame.pack(pady=20)

        name_label = tk.Label(
            name_frame,
            text="Enter your name:",
            font=("Arial", 12),
            bg=THEME["bg"],
            fg=THEME["text"],
        )
        name_label.pack(side=tk.LEFT, padx=(0, 10))

        self.name_entry = tk.Entry(
            name_frame,
            font=("Arial", 12),
            width=30,
            bg=THEME["card_bg"],
            fg=THEME["text"],
            insertbackground=THEME["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=THEME["card_bg"],
            highlightcolor=THEME["accent"],
        )
        self.name_entry.pack(side=tk.LEFT)
        self.name_entry.focus()

        buttons_frame = tk.Frame(self.frame, bg=THEME["bg"])
        buttons_frame.pack(pady=30)

        start_button = tk.Button(
            buttons_frame,
            text="Start Game",
            command=self.handle_start,
            font=("Arial", 14, "bold"),
            bg=THEME["accent"],
            fg=THEME["bg"],
            activebackground=THEME["text"],
            activeforeground=THEME["bg"],
            relief=tk.FLAT,
            padx=24,
            pady=10,
            cursor="hand2",
        )
        start_button.pack(side=tk.LEFT, padx=8)

        statistics_button = tk.Button(
            buttons_frame,
            text="Statistics",
            command=self.handle_statistics,
            font=("Arial", 14),
            bg=THEME["card_bg"],
            fg=THEME["text"],
            activebackground=THEME["bg"],
            activeforeground=THEME["text"],
            relief=tk.FLAT,
            padx=24,
            pady=10,
            cursor="hand2",
        )
        statistics_button.pack(side=tk.LEFT, padx=8)

        if self.on_back_to_dashboard:
            back_button = tk.Button(
                buttons_frame,
                text="Back to Dashboard",
                command=self.on_back_to_dashboard,
                font=("Arial", 14),
                bg=THEME["card_bg"],
                fg=THEME["text"],
                activebackground=THEME["bg"],
                activeforeground=THEME["text"],
                relief=tk.FLAT,
                padx=24,
                pady=10,
                cursor="hand2",
            )
            back_button.pack(side=tk.LEFT, padx=8)

        instructions = tk.Label(
            self.frame,
            text="🚗 Analyze the traffic network\n"
            "🔢 Calculate maximum flow (vehicles/minute)\n"
            "✅ Submit your answer to win!",
            font=("Arial", 14),
            bg=THEME["bg"],
            fg=THEME["secondary_text"],
            justify=tk.CENTER,
        )
        instructions.pack(pady=20)

        self.name_entry.bind("<Return>", lambda event: self.handle_start())

    def destroy(self):
        """Destroy the start screen."""
        self.frame.destroy()

    def handle_start(self):
        """Handle the start button click."""
        try:
            player_name = self.name_entry.get().strip()

            if not player_name:
                error_label = tk.Label(
                    self.frame,
                    text="Please enter your name!",
                    fg=ERROR_FG,
                    bg=THEME["bg"],
                    font=("Arial", 10),
                )
                error_label.pack(pady=5)
                self.root.after(2000, error_label.destroy)
                return

            print(f"Starting game with player: {player_name}")  # Debug
            self.on_start(player_name)
        except Exception as e:
            print(f"Error in handle_start: {e}")
            import traceback

            traceback.print_exc()

    def handle_statistics(self):
        """Handle statistics button click."""
        if self.on_statistics is not None:
            self.on_statistics()
