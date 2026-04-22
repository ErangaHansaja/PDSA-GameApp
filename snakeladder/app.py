import tkinter as tk
from database.snakeladder import create_table, save_winner
from tkinter import messagebox
from board import Board
from game_logic import bfs_min_moves, dijkstra_min_moves
import random
import math

# --- MODERN COLOR PALETTE ---
ACCENT = "#3498db"
SUCCESS = "#2ecc71"
DANGER = "#e74c3c"
BG_DARK = "#1a1a2e"
BG_LIGHT = "#16213e"
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

        correct_answer, forced_path, algo_perf["bfs"] = bfs_min_moves(board)
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
    if row % 2 == 1:
        col = size - 1 - col
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

    for s, e in board.ladders.items():
        draw_asset(s, e, "ladder")
    for s, e in board.snakes.items():
        draw_asset(s, e, "snake")

    draw_player()
    board_frame.pack(pady=20)

def draw_player():
    global player_token
    x, y = get_cell_coords(player_pos)
    if player_token:
        canvas.delete(player_token)
    player_token = canvas.create_oval(x-14, y-14, x+14, y+14, fill=GOLD, outline="white", width=2)

def show_question():
    global options
    options = [correct_answer]

    while len(options) < 3:
        val = random.randint(max(1, correct_answer - 3), correct_answer + 3)
        if val not in options:
            options.append(val)

    random.shuffle(options)

    for i in range(3):
        option_buttons[i].config(text=f"{options[i]} Throws", value=options[i], bg=BG_LIGHT, fg="white")

    question_frame.pack(pady=10)
    dice_label.config(text="🎲 ?", fg=TEXT_COLOR)
    dice_label.pack()

def check_answer():
    if selected_option.get() == 0:
        return
    question_frame.pack_forget()
    perform_move(selected_option.get())

def perform_move(total_moves):
    global current_move

    if current_move >= total_moves:
        show_final_result()
        return

    if total_moves == correct_answer:
        dice = forced_path[current_move]
    else:
        dice = random.randint(1, 6)

    dice_label.config(text=f"🎲 {dice}", fg=GOLD)
    move_step_by_step(dice, total_moves)

def move_step_by_step(steps, total_moves):
    global player_pos, current_move

    if steps == 0:
        if player_pos in board.snakes:
            player_pos = board.snakes[player_pos]
        elif player_pos in board.ladders:
            player_pos = board.ladders[player_pos]

        draw_player()
        current_move += 1
        root.after(600, lambda: perform_move(total_moves))
        return

    if player_pos < board.total_cells:
        player_pos += 1
        draw_player()
        root.after(150, lambda: move_step_by_step(steps - 1, total_moves))

def show_final_result():
    question_frame.pack_forget()
    dice_label.pack_forget()

    user_guess = selected_option.get()

    if user_guess == correct_answer:
        result_label.config(
            text="TOTAL VICTORY!\nPrediction correct & reached the end!",
            fg=SUCCESS
        )
        save_winner(player_name, correct_answer, board.size,
                    algo_perf["bfs"], algo_perf["dijkstra"])
    else:
        result_label.config(
            text=f"MISSED IT!\nShortest path was {correct_answer}",
            fg=DANGER
        )

    result_frame.pack(pady=20)

# -------------------- UI --------------------

name_frame = tk.Frame(root, bg=BG_DARK)
tk.Label(name_frame, text="SNAKE & LADDER\nMASTER",
         font=("Impact", 42), bg=BG_DARK, fg=GOLD).pack(pady=30)

name_entry = tk.Entry(name_frame, font=("Segoe UI", 16),
                      justify='center', bg=BG_LIGHT,
                      fg="white", insertbackground="white", bd=0)
name_entry.pack(pady=20, ipady=10, ipadx=10)

create_styled_button(name_frame, "Enter Your Name", start_game, SUCCESS).pack()
name_frame.pack(pady=100)

size_frame = tk.Frame(root, bg=BG_DARK)
tk.Label(size_frame, text="CHOOSE YOUR BOARD",
         font=HEADER_FONT, bg=BG_DARK, fg=TEXT_COLOR).pack(pady=20)

size_var = tk.StringVar(value="8")
sz_menu = tk.OptionMenu(size_frame, size_var, *[str(i) for i in range(6, 13)])
sz_menu.config(bg=BG_LIGHT, fg="white", font=PRIMARY_FONT, relief="flat")
sz_menu.pack(pady=20)

create_styled_button(size_frame, "GENERATE WORLD", select_size, ACCENT).pack()

board_frame = tk.Frame(root, bg="#111", padx=10, pady=10)
canvas = tk.Canvas(board_frame, width=500, height=500, bg="#111", highlightthickness=0)
canvas.pack()

dice_label = tk.Label(root, text="🎲", font=DICE_FONT, bg=BG_DARK, fg=GOLD)

question_frame = tk.Frame(root, bg=BG_DARK)
tk.Label(question_frame, text="MINIMUM THROWS TO WIN?",
         font=("Segoe UI Semibold", 14),
         bg=BG_DARK, fg="#bdc3c7").pack()

selected_option = tk.IntVar()

btn_container = tk.Frame(question_frame, bg=BG_DARK)
btn_container.pack(pady=20)

option_buttons = [
    tk.Radiobutton(btn_container, text="", variable=selected_option,
                   font=("Segoe UI Bold", 12), indicatoron=0,
                   width=12, selectcolor=ACCENT, cursor="hand2")
    for _ in range(3)
]

for b in option_buttons:
    b.pack(side=tk.LEFT, padx=10, ipady=5)

create_styled_button(question_frame, "CONFIRM PREDICTION", check_answer, GOLD).pack(pady=10)

result_frame = tk.Frame(root, bg=BG_DARK)
result_label = tk.Label(result_frame, text="", font=HEADER_FONT,
                        bg=BG_DARK, justify="center")
result_label.pack(pady=20)

create_styled_button(result_frame, "PLAY AGAIN", restart_game, SUCCESS).pack()