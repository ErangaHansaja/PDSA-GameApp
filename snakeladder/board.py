import random

class Board:
    def __init__(self, size):
        self.size = size
        self.total_cells = size * size
        self.snakes = {}
        self.ladders = {}
        self.generate_board()

    def generate_board(self):
        count = self.size - 2

        # 1. Generate ladders
        while len(self.ladders) < count:
            start = random.randint(1, self.total_cells - 2)
            end = random.randint(start + 1, self.total_cells)

            if start not in self.ladders:
                self.ladders[start] = end

        # 2. Generate snakes
        while len(self.snakes) < count:
            start = random.randint(2, self.total_cells - 1)
            end = random.randint(1, start - 1)

            # Check: Head of snake cannot be the start of a ladder
            # Check: Head of snake should also not be the end of a ladder 
            if start not in self.snakes and start not in self.ladders:
                self.snakes[start] = end