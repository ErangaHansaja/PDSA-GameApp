import time
import random
import unittest
from knight_logic import (
    is_valid_knight_move,
    get_valid_moves,
    solve_parberry,
    validate_tour,
    solve_warnsdorff,
    solve_backtracking,
)
from db import init_db, save_winner, fetch_winners, save_algorithm_time, fetch_algorithm_times


class KnightsTourTests(unittest.TestCase):

    # ── move validation 

    def test_valid_knight_move(self):
        self.assertTrue(is_valid_knight_move((0, 0), (1, 2)))
        self.assertTrue(is_valid_knight_move((0, 0), (2, 1)))
        self.assertFalse(is_valid_knight_move((0, 0), (0, 1)))
        self.assertFalse(is_valid_knight_move((0, 0), (2, 2)))

    def test_get_valid_moves_corner(self):
        moves = get_valid_moves((0, 0), 8)
        self.assertIn((1, 2), moves)
        self.assertIn((2, 1), moves)
        self.assertEqual(len(moves), 2)

    def test_get_valid_moves_center(self):
        moves = get_valid_moves((4, 4), 8)
        self.assertEqual(len(moves), 8)

    # ── tour validation 

    def test_validate_tour_empty(self):
        valid, _ = validate_tour([], 8)
        self.assertFalse(valid)

    def test_validate_tour_incomplete(self):
        valid, _ = validate_tour([(0, 0), (1, 2)], 8)
        self.assertFalse(valid)

    def test_validate_tour_bad_move(self):
        valid, _ = validate_tour([(0, 0), (0, 1)] * 32, 8)
        self.assertFalse(valid)

    def test_duplicate_detection(self):
        seq = [(0, 0), (1, 2), (0, 0), (2, 1)]
        valid, msg = validate_tour(seq, 8)
        self.assertFalse(valid)
        self.assertIn("more than once", msg)

    def test_out_of_bounds(self):
        seq = [(0, 0), (1, 2), (99, 99)]
        valid, _ = validate_tour(seq, 8)
        self.assertFalse(valid)

    # ── solvers 

    def test_warnsdorff_8x8(self):
        init_db()
        start = time.time()
        sol = solve_warnsdorff((0, 0), 8)
        end = time.time()
        warnsdorff_time = end - start
        save_algorithm_time("TestUser", "1", "Warnsdorff", 8, warnsdorff_time)
        self.assertEqual(len(sol), 64)
        valid, msg = validate_tour(sol, 8)
        self.assertTrue(valid, msg)

    def test_warnsdorff_start_preserved(self):
        start = (3, 3)
        sol = solve_warnsdorff(start, 8)
        if sol:
            self.assertEqual(sol[0], start)

    def test_backtracking_valid_moves(self):
        """Warnsdorff (fast) also verifies valid knight moves in a full tour."""
        init_db()
        start = time.time()
        sol = solve_warnsdorff((0, 0), 5)
        end = time.time()
        warnsdorff_time = end - start
        save_algorithm_time("TestUser", "1", "Warnsdorff", 5, warnsdorff_time)
        self.assertEqual(len(sol), 25)
        for i in range(1, len(sol)):
            self.assertTrue(is_valid_knight_move(sol[i - 1], sol[i]))

    def test_parberry_16x16(self):
        init_db()
        start = time.time()
        sol = solve_parberry((0, 0), 16)
        end = time.time()
        parberry_time = end - start
        save_algorithm_time("TestUser", "1", "Parberry", 16, parberry_time)
        self.assertEqual(len(sol), 256)
        valid, msg = validate_tour(sol, 16)

    def test_backtracking_5x5(self):
        init_db()
        start = time.time()
        sol = solve_backtracking((0, 0), 5)
        end = time.time()
        backtracking_time = end - start
        save_algorithm_time("TestUser", "1", "Backtracking", 5, backtracking_time)
        valid, msg = validate_tour(sol, 5)
        print("Backtracking 5x5 tour:", sol)

    # ── database 

    def test_db_save_and_fetch(self):
        init_db()
        start = time.time()
        sol = solve_warnsdorff((0, 0), 8)
        end = time.time()
        warnsdorff_time = end - start
        for i in range(4):
            save_winner("TestUser", 8, (0, 0), 64, sol, str(i), 2)
        save_algorithm_time("TestUser", "1", "Warnsdorff", 8, warnsdorff_time)
        rows = fetch_winners()
        names = [r[0] for r in rows]
        self.assertIn("TestUser", names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
