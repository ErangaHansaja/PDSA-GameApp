import tkinter as tk
from database import create_table, save_winner
from tkinter import messagebox
from board import Board
from game_logic import bfs_min_moves, dijkstra_min_moves
import random
import math

# --------------
# Pathushi
# ------------
# --- MODERN COLOR PALETTE ---
ACCENT = "#3498db"      # Bright Blue
SUCCESS = "#2ecc71"     # Emerald Green
DANGER = "#e74c3c"      # Alizarin Red
BG_DARK = "#1a1a2e"     # Deep Navy
BG_LIGHT = "#16213e"    # Lighter Navy
TEXT_COLOR = "#e9ecef"
GOLD = "#f1c40f"

# --- UI CONFIGURATION ---
PRIMARY_FONT = ("Segoe UI", 12)
HEADER_FONT = ("Segoe UI Semibold", 24)
DICE_FONT = ("Segoe UI Bold", 32)

root = tk.Tk()
root.title("Snake & Ladder Master")
root.geometry("650x950")
root.configure(bg=BG_DARK)

# Ensure database table exists
create_table()

# Global variables
player_name = ""
board = None
correct_answer = 0
player_pos = 1
player_token = None
current_move = 0
forced_path = []
algo_perf = {"bfs": 0, "dijkstra": 0}

# -------------------- STYLIZED BUTTON HELPER --------------------

def create_styled_button(parent, text, command, color=ACCENT):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg="white", font=("Segoe UI Bold", 11),
        activebackground="#ffffff", activeforeground=color,
        relief="flat", padx=20, pady=8, cursor="hand2", bd=0
    )
    btn.bind("<Enter>", lambda e: btn.config(bg="#ffffff", fg=color))
    btn.bind("<Leave>", lambda e: btn.config(bg=color, fg="white"))
    return btn

# -------------------- DRAWING ASSETS --------------------

def draw_asset(start, end, type):
    x1, y1 = get_cell_coords(start)
    x2, y2 = get_cell_coords(end)

    if type == "ladder":
        angle = math.atan2(y2 - y1, x2 - x1)
        offset_x = 8 * math.sin(angle)
        offset_y = 8 * math.cos(angle)
        canvas.create_line(x1 - offset_x, y1 + offset_y, x2 - offset_x, y2 + offset_y, fill="#d35400", width=4)
        canvas.create_line(x1 + offset_x, y1 - offset_y, x2 + offset_x, y2 - offset_y, fill="#d35400", width=4)
        
        num_rungs = 8
        for i in range(num_rungs + 1):
            frac = i / num_rungs
            lx, ly = (x1 - offset_x) + frac * (x2 - x1), (y1 + offset_y) + frac * (y2 - y1)
            rx, ry = (x1 + offset_x) + frac * (x2 - x1), (y1 - offset_y) + frac * (y2 - y1)
            canvas.create_line(lx, ly, rx, ry, fill="#e67e22", width=2)

    elif type == "snake":
        canvas.create_line(x1, y1, x2, y2, fill=SUCCESS, width=12, capstyle=tk.ROUND, smooth=True)
        canvas.create_oval(x1-10, y1-10, x1+10, y1+10, fill="#27ae60", outline="white")
        canvas.create_oval(x1-4, y1-4, x1-1, y1-1, fill="white")
        canvas.create_oval(x1+1, y1-4, x1+4, y1-1, fill="white")
        


# -------------------- CORE LOGIC --------------------

def restart_game():
    global player_pos, current_move, player_token, board, forced_path
    player_pos = 1
    current_move = 0
    player_token = None
    board = None
    forced_path = []
    selected_option.set(0)
    
    canvas.delete("all")
    for frame in [result_frame, board_frame, size_frame, question_frame]:
        frame.pack_forget()
    dice_label.pack_forget()
    
    name_entry.delete(0, tk.END)
    name_frame.pack(pady=100)

def start_game():
    global player_name
    player_name = name_entry.get().strip()
    if not player_name:
        messagebox.showwarning("Name Required", "Please enter your hero name!")
        return
    name_frame.pack_forget()
    size_frame.pack(pady=100)

def select_size():
    global board, correct_answer, forced_path, algo_perf
    try:
        size = int(size_var.get())
        board = Board(size)
        
        # Requirement: Use two algorithms and record time
        # Algo 1: BFS
        correct_answer, forced_path, algo_perf["bfs"] = bfs_min_moves(board)
        
        # Algo 2: Dijkstra
        _, algo_perf["dijkstra"] = dijkstra_min_moves(board)
        
        size_frame.pack_forget()
        draw_board()
        show_question()
    except Exception as e:
        messagebox.showerror("System Error", f"Failed to initialize board: {e}")

def get_cell_coords(cell_num):
    size = board.size
    cell_size = 500 // size
    row = (cell_num - 1) // size
    col = (cell_num - 1) % size
    if row % 2 == 1: col = size - 1 - col
    x = col * cell_size + cell_size // 2
    y = (size - row - 1) * cell_size + cell_size // 2
    return x, y

def draw_board():
    canvas.delete("all")
    size = board.size
    cell_size = 500 // size
    for row in range(size):
        for col in range(size):
            cell_num = (row * size + col + 1) if row % 2 == 0 else (row * size + (size - col))
            x1, y1 = col * cell_size, (size - row - 1) * cell_size
            color = "#2c3e50" if (row + col) % 2 == 0 else "#34495e"
            canvas.create_rectangle(x1, y1, x1+cell_size, y1+cell_size, fill=color, outline="#1a1a2e")
            canvas.create_text(x1 + 15, y1 + 15, text=str(cell_num), fill="#95a5a6", font=("Arial", 9))

    for s, e in board.ladders.items(): draw_asset(s, e, "ladder")
    for s, e in board.snakes.items(): draw_asset(s, e, "snake")
    draw_player()
    board_frame.pack(pady=20)