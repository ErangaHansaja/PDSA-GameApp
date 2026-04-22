import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def open_snake_ladder(root):
    root.destroy()
    from snakeladder.app import root as game_root
    game_root.mainloop()
