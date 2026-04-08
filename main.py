# Launches the dashboard UI - main entry point
import tkinter as tk
from tkinter import messagebox


def show_coming_soon(game_name):
    messagebox.showinfo(game_name, "Coming Soon")


def main():
    root = tk.Tk()
    root.title("PDSA Game Suite")
    root.geometry("400x350")
    root.resizable(False, False)

    tk.Label(root, text="PDSA Game Suite", font=("Arial", 18, "bold")).pack(pady=20)

    games = [
        "Minimum Cost",
        "Snake and Ladder",
        "Traffic Simulation",
        "Knight's Tour",
        "Sixteen Queens",
    ]

    for game in games:
        tk.Button(
            root,
            text=game,
            width=25,
            height=2,
            command=lambda g=game: show_coming_soon(g),
        ).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
