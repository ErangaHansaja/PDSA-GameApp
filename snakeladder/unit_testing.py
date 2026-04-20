import unittest
from board import Board
from game_logic import bfs_min_moves

class TestSnakeLadder(unittest.TestCase):
    def setUp(self):
        self.board = Board(6)

    def test_board_size(self):
        self.assertEqual(self.board.total_cells, 36)

    def test_logic_returns_path(self):
        count, path, time_taken = bfs_min_moves(self.board)
        self.assertGreater(count, 0)
        self.assertEqual(len(path), count)

    def test_snake_and_ladder_counts(self):
        # N-2 requirement
        self.assertEqual(len(self.board.snakes), 4)
        self.assertEqual(len(self.board.ladders), 4)

if __name__ == "__main__":
    unittest.main()