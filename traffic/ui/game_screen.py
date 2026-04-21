import tkinter as tk
from tkinter import messagebox
from graph_generator import NODE_POSITIONS

# Professional color palette
THEME = {
    "bg": "#1a1a2e",
    "sidebar": "#16213e",
    "accent": "#4cc9f0",
    "text": "#ffffff",
    "node_a": "#90EE90",  # Light green for source
    "node_t": "#FFB6C1",  # Light red for sink
    "node_mid": "#87CEEB",  # Light blue
    "card_bg": "#0f3460",
}

# Readable secondary text on dark cards (not in THEME keys)
TEXT_MUTED = "#9eb8d0"
# Light surface for the graph (contrast with network drawing)
CANVAS_BG = "#eef2fa"


class GameScreen:
    """Game screen showing the graph and answer input."""

    def __init__(self, root, on_submit, round_number, on_back_to_dashboard=None):
        """
        Initialize the game screen.

        Args:
            root: Tkinter root window
            on_submit: Callback function when answer is submitted (receives answer)
            round_number: Current round number
            on_back_to_dashboard: Optional callback when Back (to dashboard) is clicked
        """
        self.root = root
        self.on_submit = on_submit
        self.round_number = round_number
        self.on_back_to_dashboard = on_back_to_dashboard

        self.frame = tk.Frame(root, bg=THEME["bg"], padx=20, pady=20)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.build_ui()

    def build_ui(self):
        """Build the game screen UI."""
        main_container = tk.Frame(self.frame, bg=THEME["bg"])
        main_container.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_container, bg=THEME["bg"])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        top_frame = tk.Frame(left_frame, bg=THEME["bg"])
        top_frame.pack(fill=tk.X, pady=(0, 10))

        back_button = tk.Button(
            top_frame,
            text="Back",
            command=self.handle_back_to_dashboard,
            font=("Arial", 11, "bold"),
            bg=THEME["sidebar"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground=THEME["text"],
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
        )
        back_button.pack(side=tk.LEFT, padx=(0, 12))

        round_label = tk.Label(
            top_frame,
            text=f"Round {self.round_number}",
            font=("Arial", 16, "bold"),
            bg=THEME["bg"],
            fg=THEME["text"],
        )
        round_label.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(
            left_frame,
            width=700,
            height=450,
            bg=CANVAS_BG,
            relief=tk.SOLID,
            borderwidth=2,
            highlightthickness=0,
        )
        self.canvas.pack(pady=10)

        answer_frame = tk.Frame(left_frame, bg=THEME["bg"])
        answer_frame.pack(pady=20)

        answer_label = tk.Label(
            answer_frame,
            text="Enter the maximum flow from A (source) to T (sink):",
            font=("Arial", 12),
            bg=THEME["bg"],
            fg=THEME["text"],
        )
        answer_label.pack(side=tk.LEFT, padx=(0, 10))

        self.answer_entry = tk.Entry(
            answer_frame,
            font=("Arial", 14),
            width=10,
            justify=tk.CENTER,
            bg=THEME["sidebar"],
            fg=THEME["text"],
            insertbackground=THEME["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=THEME["card_bg"],
            highlightcolor=THEME["accent"],
        )
        self.answer_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.answer_entry.focus()

        submit_button = tk.Button(
            answer_frame,
            text="Submit",
            command=self.handle_submit,
            font=("Arial", 12, "bold"),
            bg=THEME["accent"],
            fg=THEME["bg"],
            activebackground=THEME["text"],
            activeforeground=THEME["bg"],
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
        )
        submit_button.pack(side=tk.LEFT, padx=(0, 10))

        clear_button = tk.Button(
            answer_frame,
            text="Clear",
            command=self.handle_clear,
            font=("Arial", 12),
            bg=THEME["sidebar"],
            fg=THEME["text"],
            activebackground=THEME["card_bg"],
            activeforeground=THEME["text"],
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
        )
        clear_button.pack(side=tk.LEFT)

        self.answer_entry.bind("<Return>", lambda event: self.handle_submit())

        tips_frame = tk.LabelFrame(
            left_frame,
            text="How to play",
            font=("Arial", 10, "bold"),
            fg=THEME["accent"],
            bg=THEME["card_bg"],
            padx=12,
            pady=10,
            highlightthickness=0,
            borderwidth=1,
            relief=tk.GROOVE,
        )
        tips_frame.pack(fill=tk.X, pady=(10, 0))
        tips_frame.configure(labelanchor="nw")

        tips_lines = (
            "• Green A = source, pink T = sink; arrows show direction; numbers are capacities.\n"
            "• Type the maximum flow (whole number ≥ 0), then Submit or press Enter.\n"
            "• Exact answer = Win; within ±1 = Draw; otherwise Lose.\n"
            "• Clear removes your guess from the box."
        )
        tk.Label(
            tips_frame,
            text=tips_lines,
            font=("Arial", 9),
            bg=THEME["card_bg"],
            fg=TEXT_MUTED,
            justify=tk.LEFT,
            anchor="w",
        ).pack(anchor="w")

        right_frame = tk.Frame(main_container, width=250, bg=THEME["sidebar"])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        stats_frame = tk.LabelFrame(
            right_frame,
            text="Game Stats",
            font=("Arial", 10, "bold"),
            fg=THEME["accent"],
            bg=THEME["card_bg"],
            padx=15,
            pady=15,
            highlightthickness=0,
            borderwidth=1,
            relief=tk.GROOVE,
        )
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        stats_frame.configure(labelanchor="n")

        self.last_winner_label = tk.Label(
            stats_frame,
            text="Last Winner: N/A",
            font=("Arial", 10),
            bg=THEME["card_bg"],
            fg=THEME["text"],
        )
        self.last_winner_label.pack(anchor=tk.W, pady=5)

        self.last_answer_label = tk.Label(
            stats_frame,
            text="Last Answer: N/A",
            font=("Arial", 10),
            bg=THEME["card_bg"],
            fg=THEME["text"],
        )
        self.last_answer_label.pack(anchor=tk.W, pady=5)

        self.avg_time_label = tk.Label(
            stats_frame,
            text="Avg Calculation Time: N/A",
            font=("Arial", 10),
            bg=THEME["card_bg"],
            fg=THEME["text"],
        )
        self.avg_time_label.pack(anchor=tk.W, pady=5)

        algo_frame = tk.LabelFrame(
            right_frame,
            text="Algorithm Results",
            font=("Arial", 10, "bold"),
            fg=THEME["accent"],
            bg=THEME["card_bg"],
            padx=15,
            pady=15,
            highlightthickness=0,
            borderwidth=1,
            relief=tk.GROOVE,
        )
        algo_frame.pack(fill=tk.X, pady=(0, 20))
        algo_frame.configure(labelanchor="n")

        self.correct_answer_label = tk.Label(
            algo_frame,
            text="Max Flow: N/A",
            font=("Arial", 12, "bold"),
            bg=THEME["card_bg"],
            fg=THEME["accent"],
        )
        self.correct_answer_label.pack(anchor=tk.W, pady=5)

        self.algo1_time_label = tk.Label(
            algo_frame,
            text="Ford-Fulkerson: N/A",
            font=("Arial", 9),
            bg=THEME["card_bg"],
            fg=TEXT_MUTED,
        )
        self.algo1_time_label.pack(anchor=tk.W, pady=3)

        self.algo2_time_label = tk.Label(
            algo_frame,
            text="Edmonds-Karp: N/A",
            font=("Arial", 9),
            bg=THEME["card_bg"],
            fg=TEXT_MUTED,
        )
        self.algo2_time_label.pack(anchor=tk.W, pady=3)

    def handle_back_to_dashboard(self):
        """Invoked by Back; connect `on_back_to_dashboard` from the app host (e.g. dashboard)."""
        if self.on_back_to_dashboard is not None:
            self.on_back_to_dashboard()

    def draw_graph(self, capacities):
        """
        Draw the graph on the canvas.

        Args:
            capacities: Dictionary of edge capacities
        """
        self.capacities = capacities

        self.canvas.delete("all")

        for (from_node, to_node), capacity in capacities.items():
            self.draw_edge(from_node, to_node, capacity)

        for node, (x, y) in NODE_POSITIONS.items():
            self.draw_node(node, x, y)

    def draw_node(self, node, x, y):
        """
        Draw a single node on the canvas.

        Args:
            node: Node name (A, B, C, etc.)
            x: X coordinate
            y: Y coordinate
        """
        radius = 25

        if node == "A":
            fill_color = THEME["node_a"]
        elif node == "T":
            fill_color = THEME["node_t"]
        else:
            fill_color = THEME["node_mid"]

        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=fill_color,
            outline=THEME["sidebar"],
            width=3,
        )

        self.canvas.create_text(
            x,
            y,
            text=node,
            font=("Arial", 16, "bold"),
            fill=THEME["bg"],
        )

    def draw_edge(self, from_node, to_node, capacity):
        """
        Draw an edge with capacity label on the canvas.

        Args:
            from_node: Source node of the edge
            to_node: Destination node of the edge
            capacity: Edge capacity
        """
        x1, y1 = NODE_POSITIONS[from_node]
        x2, y2 = NODE_POSITIONS[to_node]

        radius = 25

        dx = x2 - x1
        dy = y2 - y1
        length = (dx**2 + dy**2) ** 0.5

        if length == 0:
            return

        short_x1 = x1 + (dx / length) * radius
        short_y1 = y1 + (dy / length) * radius
        short_x2 = x2 - (dx / length) * radius
        short_y2 = y2 - (dy / length) * radius

        self.canvas.create_line(
            short_x1,
            short_y1,
            short_x2,
            short_y2,
            arrow=tk.LAST,
            fill=THEME["sidebar"],
            width=3,
        )

        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        offset_edges = {
            ("B", "F"): (15, -15),
            ("C", "E"): (-15, 15),
            ("A", "C"): (0, -15),
            ("E", "H"): (15, 0),
            ("F", "H"): (15, 15),
        }

        edge_key = (from_node, to_node)
        if edge_key in offset_edges:
            offset_x, offset_y = offset_edges[edge_key]
            mid_x += offset_x
            mid_y += offset_y

        bg_width = 30
        bg_height = 22
        self.canvas.create_rectangle(
            mid_x - bg_width / 2,
            mid_y - bg_height / 2,
            mid_x + bg_width / 2,
            mid_y + bg_height / 2,
            fill=CANVAS_BG,
            outline=THEME["card_bg"],
            width=2,
        )

        self.canvas.create_text(
            mid_x,
            mid_y,
            text=str(capacity),
            font=("Arial", 13, "bold"),
            fill=THEME["card_bg"],
        )

    def handle_submit(self):
        """Handle the submit button click."""
        try:
            answer = self.answer_entry.get().strip()
            print(f"Submit clicked, answer: {answer}")  # Debug

            if not answer:
                print("Empty answer")  # Debug
                messagebox.showwarning("Empty Input", "Please enter your answer!")
                return

            try:
                answer_int = int(answer)
                if answer_int < 0:
                    print("Negative answer")  # Debug
                    messagebox.showwarning(
                        "Invalid Input",
                        "Please enter a positive number!",
                    )
                    return
                print(f"Submitting answer: {answer_int}")  # Debug
                self.on_submit(answer_int)
            except ValueError:
                print(f"Invalid answer: {answer}")  # Debug
                messagebox.showwarning(
                    "Invalid Input",
                    f"'{answer}' is not a valid number!\nPlease enter a whole number.",
                )
        except Exception as e:
            print(f"Error in handle_submit: {e}")
            import traceback

            traceback.print_exc()

    def handle_clear(self):
        """Handle the clear button click - clears the answer input."""
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus()

    def destroy(self):
        """Destroy the game screen."""
        self.frame.destroy()

    def update_stats(self, last_winner=None, last_answer=None, avg_time=None):
        """
        Update the game stats panel.

        Args:
            last_winner: Name of the last winner
            last_answer: Last correct answer value
            avg_time: Average calculation time
        """
        if last_winner:
            self.last_winner_label.config(text=f"Last Winner: {last_winner}")

        if last_answer is not None:
            self.last_answer_label.config(text=f"Last Answer: {last_answer}")

        if avg_time is not None:
            self.avg_time_label.config(text=f"Avg Calc Time: {avg_time:.4f}s")

    def update_algorithm_results(self, correct_answer, algo1_time, algo2_time):
        """
        Update the algorithm results display.

        Args:
            correct_answer: The correct maximum flow value
            algo1_time: Ford-Fulkerson execution time
            algo2_time: Edmonds-Karp execution time
        """
        self.correct_answer_label.config(text=f"Max Flow: {correct_answer}")
        self.algo1_time_label.config(text=f"Ford-Fulkerson: {algo1_time:.8f}s")
        self.algo2_time_label.config(text=f"Edmonds-Karp: {algo2_time:.8f}s")
