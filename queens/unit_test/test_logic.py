import unittest
from logic import NQueensLogic


class TestNQueensLogic(unittest.TestCase):
    def setUp(self):
        # Initialize with a smaller max_solutions to keep tests fast
        self.logic = NQueensLogic(size=16, max_solutions=5)

    def test_is_valid_safe_placement(self):
        # Queens that don't threaten each other
        queens = [(0, 0), (1, 2), (2, 4)]
        self.assertTrue(self.logic.is_valid(queens))

    def test_is_valid_same_row(self):
        # Queens on the same row (0)
        queens = [(0, 0), (0, 5)]
        self.assertFalse(self.logic.is_valid(queens))

def test_is_valid_same_column(self):
        # Queens on the same column (0)
        queens = [(0, 0), (5, 0)]
        self.assertFalse(self.logic.is_valid(queens))

    def test_is_valid_diagonal(self):
        # Queens on the same diagonal
        queens = [(0, 0), (2, 2)]
        self.assertFalse(self.logic.is_valid(queens))

    def test_run_sequential_returns_correct_types(self):
        # Test if the solver actually runs and returns a tuple
        count, time_taken, solutions = self.logic.run_sequential()
        self.assertIsInstance(count, int)
        self.assertIsInstance(time_taken, float)
        self.assertIsInstance(solutions, list)


if __name__ == "__main__":
    unittest.main()
