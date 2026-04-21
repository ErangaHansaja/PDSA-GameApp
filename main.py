# Launches the dashboard UI - main entry point
import tkinter as tk
from tkinter import messagebox


def show_coming_soon(game_name):
    messagebox.showinfo(game_name, "Coming Soon")


def launch_game(game_name, root):
    if game_name == "Traffic Simulation":
        root.destroy()
        
        import sys
        import os
        traffic_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "traffic")
        if traffic_dir not in sys.path:
            sys.path.insert(0, traffic_dir)
            
        from traffic.main import MaximumFlowGame
        app = MaximumFlowGame()
        
        # Override the handler to go back to dashboard
        def go_back():
            app.root.destroy()
            main()
            
        app.handle_back_to_dashboard = go_back
        app.run()
    else:
        show_coming_soon(game_name)


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
            command=lambda g=game: launch_game(g, root),
        ).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
