class Player:
    def __init__(self, name):
        self.name = name
        self.position = 1

    def move(self, steps, board):
        self.position += steps

        if self.position > board.total_cells:
            self.position = board.total_cells

        # Snake or ladder
        if self.position in board.snakes:
            print(f"🐍 Snake! {self.position} → {board.snakes[self.position]}")
            self.position = board.snakes[self.position]

        elif self.position in board.ladders:
            print(f"🪜 Ladder! {self.position} → {board.ladders[self.position]}")
            self.position = board.ladders[self.position]