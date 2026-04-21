import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mincost.algorithms import generate_cost_matrix, hungarian_algorithm, greedy_algorithm, generate_choices, run_round


# ─── 1. Logic / Algorithm Tests ──────────────────────────────────────────────

class TestAlgorithms(unittest.TestCase):

    def test_matrix_dimensions_and_range(self):
        """Matrix is n×n with values in [20, 200]."""
        m = generate_cost_matrix(50)
        self.assertEqual(len(m), 50)
        self.assertTrue(all(len(r) == 50 for r in m))
        self.assertTrue(all(20 <= v <= 200 for r in m for v in r))

    def test_hungarian_known_case(self):
        """Hungarian finds optimal cost on a tiny matrix."""
        cost = [[9, 2, 7], [6, 4, 3], [5, 8, 1]]
        total, asgn = hungarian_algorithm(cost)
        self.assertEqual(total, 9)
        self.assertEqual(sorted(asgn), [0, 1, 2])

    def test_hungarian_optimality_vs_brute_force(self):
        """Hungarian matches brute-force minimum on a 4×4 matrix."""
        from itertools import permutations
        cost = [[10, 5, 13, 15], [3, 9, 18, 3], [13, 7, 4, 15], [12, 11, 14, 8]]
        h_total, _ = hungarian_algorithm(cost)
        bf_min = min(sum(cost[i][p[i]] for i in range(4)) for p in permutations(range(4)))
        self.assertEqual(h_total, bf_min)

    def test_greedy_valid_and_gte_optimal(self):
        """Greedy produces a valid assignment and cost ≥ Hungarian cost."""
        m = generate_cost_matrix(50)
        h_total, _ = hungarian_algorithm(m)
        g_total, asgn = greedy_algorithm(m)
        self.assertEqual(len(set(asgn)), 50)
        self.assertGreaterEqual(g_total, h_total)

    def test_generate_choices(self):
        """Choices always contain the correct answer, are unique, and count is 3."""
        for correct in [1000, 5000, 9999]:
            choices = generate_choices(correct)
            self.assertEqual(len(choices), 3)
            self.assertEqual(len(set(choices)), 3)
            self.assertIn(correct, choices)

    def test_run_round_structure_and_timing(self):
        """run_round returns expected keys with non-negative timing."""
        result = run_round(50)
        for key in ("n", "cost_matrix", "hungarian", "greedy"):
            self.assertIn(key, result)
        for algo in ("hungarian", "greedy"):
            self.assertGreaterEqual(result[algo]["time_ms"], 0)
            asgn = result[algo]["assignment"]
            self.assertEqual(len(set(asgn)), 50)


# ─── 2. Database Tests ───────────────────────────────────────────────────────

class TestDatabase(unittest.TestCase):

    def setUp(self):
        import database.connection as conn_module
        self._orig = conn_module.DB_PATH
        conn_module.DB_PATH = os.path.join(os.path.dirname(__file__), "test_pdsa.db")
        from database.mincost import create_tables
        create_tables()

    def tearDown(self):
        import database.connection as conn_module
        test_db = conn_module.DB_PATH
        conn_module.DB_PATH = self._orig
        for suffix in ("", "-wal", "-shm"):
            p = test_db + suffix if suffix else test_db
            if os.path.exists(p):
                os.remove(p)

    def _save(self, game_id, player, rnd=1, n=50, result="CORRECT"):
        from database.mincost import save_round
        save_round(game_id, player, rnd, n, 1500.0, 1500.0, 1500.0, 12.5, 1800.0, 2.3, result)

    def test_save_and_retrieve(self):
        from database.mincost import get_all_rounds
        self._save("g1", "Alice")
        rows = get_all_rounds()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "Alice")

    def test_multiple_rounds(self):
        from database.mincost import get_all_rounds
        self._save("g2", "Bob", rnd=1)
        self._save("g2", "Bob", rnd=2, result="WRONG")
        self.assertEqual(len(get_all_rounds()), 2)

    def test_update_overall_result(self):
        from database.mincost import update_overall_result, get_all_rounds
        self._save("g3", "Charlie")
        update_overall_result("g3", "WIN")
        self.assertEqual(get_all_rounds()[0][11], "WIN")

    def test_overall_result_null_before_update(self):
        from database.mincost import get_all_rounds
        self._save("g4", "Dave")
        self.assertIsNone(get_all_rounds()[0][11])


# ─── 3. App / UI Smoke Tests ─────────────────────────────────────────────────

class TestApp(unittest.TestCase):

    def setUp(self):
        import tkinter as tk
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_open_mincost_game_creates_window(self):
        """open_mincost_game should create a Toplevel window."""
        import tkinter as tk
        from mincost.app import MinCostGame
        game = MinCostGame(self.root)
        self.assertIsInstance(game.window, tk.Toplevel)
        game.window.destroy()

    def test_game_initial_state(self):
        """Game starts at round 0 with 0 wins and 0 losses."""
        from mincost.app import MinCostGame
        game = MinCostGame(self.root)
        self.assertEqual(game.round_number, 0)
        self.assertEqual(game.wins, 0)
        self.assertEqual(game.losses, 0)
        game.window.destroy()


if __name__ == "__main__":
    unittest.main()
