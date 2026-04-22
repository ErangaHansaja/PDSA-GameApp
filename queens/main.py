import tkinter as tk
from app import ChessApp

if __name__ == "__main__":
    # Create the root window
    root = tk.Tk()
    # Pass root to our ChessApp class
    app = ChessApp(root)
    # Start the Tkinter event loop
    root.mainloop()
