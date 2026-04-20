import tkinter as tk
from tkinter import messagebox

# Standard Knight Moves
KNIGHT_MOVES = [
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1)
]

class KnightsTourUI:
    def __init__(self, root, size=6):
        self.root = root
        self.size = size
        self.cell_size = 60
        self.canvas = tk.Canvas(root, width=size*self.cell_size, height=size*self.cell_size)
        self.canvas.pack(padx=10, pady=10)
        
        # State variables
        self.board = [[-1] * size for _ in range(size)]
        self.cells = {} # Map (r, c) to canvas rectangle ID
        self.texts = {} # Map (r, c) to canvas text ID
        self.stack = [] # (pos, move_from, move_index)
        self.path = []
        self.move_no = 0
        
        self.draw_grid()
        self.setup_tour((0, 0))
        self.run_step()

    def draw_grid(self):
        """Initializes the visual board."""
        for r in range(self.size):
            for c in range(self.size):
                color = "#eeeed2" if (r + c) % 2 == 0 else "#769656"
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                text = self.canvas.create_text(x1 + 30, y1 + 30, text="", font=("Arial", 14, "bold"))
                
                self.cells[(r, c)] = rect
                self.texts[(r, c)] = text

    def setup_tour(self, start):
        x, y = start
        self.board[x][y] = 0
        self.path = [start]
        self.move_no = 1
        self.current_pos = start
        self.move_index = -1 # Index of the last move tried from current position
        
        # Update UI for start position
        self.canvas.itemconfig(self.cells[start], fill="#f6f669") # Highlight current
        self.canvas.itemconfig(self.texts[start], text="0")

    def is_move_safe(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == -1

    def run_step(self):
        """The core recursive-like step for visualization."""
        if self.move_no >= self.size * self.size:
            messagebox.showinfo("Success", "Knight's Tour Complete!")
            return

        x, y = self.current_pos
        found = False

        # Try moves starting from the next available index
        for i in range(self.move_index + 1, 8):
            nx, ny = x + KNIGHT_MOVES[i][0], y + KNIGHT_MOVES[i][1]

            if self.is_move_safe(nx, ny):
                # Save backtracking info: (last_pos, from_pos, move_index_used)
                self.stack.append(((nx, ny), (x, y), i))
                
                # Update Logic
                self.board[nx][ny] = self.move_no
                self.path.append((nx, ny))
                self.current_pos = (nx, ny)
                self.move_no += 1
                self.move_index = -1 # Reset move index for the new square
                
                # Update UI
                self.canvas.itemconfig(self.cells[(nx, ny)], fill="#f6f669")
                self.canvas.itemconfig(self.texts[(nx, ny)], text=str(self.move_no - 1))
                found = True
                break

        if not found:
            # Backtrack
            if not self.stack:
                messagebox.showwarning("Failed", "No solution found.")
                return
            
            # Reset UI of the current failing square
            self.canvas.itemconfig(self.cells[self.current_pos], fill=self.get_orig_color(self.current_pos))
            self.canvas.itemconfig(self.texts[self.current_pos], text="")
            
            # Revert Logic
            self.board[x][y] = -1
            self.path.pop()
            self.move_no -= 1
            
            # Pop stack to go back to previous position and remember which index we failed at
            _, prev_pos, last_tried_index = self.stack.pop()
            self.current_pos = prev_pos
            self.move_index = last_tried_index
            
        # Schedule next step (200ms delay)
        self.root.after(1, self.run_step)

    def get_orig_color(self, pos):
        r, c = pos
        return "#eeeed2" if (r + c) % 2 == 0 else "#769656"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Brute Force Knight's Tour")
    # Size 5 or 6 is better for brute force; 8 takes a very long time!
    app = KnightsTourUI(root, size=5)
    root.mainloop()