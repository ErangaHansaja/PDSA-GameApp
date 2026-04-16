import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mincost.algorithms import (
    generate_cost_matrix,
    hungarian_algorithm,
    greedy_algorithm,
    generate_choices,
    run_round,
)


class TestCostMatrixGeneration(unittest.TestCase):
    """Tests for the cost matrix generator."""

    def test_matrix_dimensions(self):
        for n in [5, 10, 50]:
            matrix = generate_cost_matrix(n)
            self.assertEqual(len(matrix), n)
            for row in matrix:
                self.assertEqual(len(row), n)

    def test_cost_range(self):
        matrix = generate_cost_matrix(50)
        for row in matrix:
            for val in row:
                self.assertGreaterEqual(val, 20)
                self.assertLessEqual(val, 200)

    def test_randomness(self):
        m1 = generate_cost_matrix(50)
        m2 = generate_cost_matrix(50)
        self.assertNotEqual(m1, m2)


class TestHungarianAlgorithm(unittest.TestCase):
    """Tests for the Hungarian (optimal) algorithm."""

    def test_small_known_case(self):
        # 3x3 matrix with known optimal solution
        cost = [
            [9, 2, 7],
            [6, 4, 3],
            [5, 8, 1],
        ]
        total, assignment = hungarian_algorithm(cost)
        # Optimal: emp0->task1(2), emp1->task0(6), emp2->task2(1) = 9
        self.assertEqual(total, 9)
        # Verify assignment is valid (each task assigned once)
        self.assertEqual(sorted(assignment), [0, 1, 2])

    def test_identity_matrix_style(self):
        # Diagonal is cheapest
        cost = [
            [1, 100, 100],
            [100, 1, 100],
            [100, 100, 1],
        ]
        total, assignment = hungarian_algorithm(cost)
        self.assertEqual(total, 3)
        self.assertEqual(assignment, [0, 1, 2])

    def test_single_element(self):
        cost = [[42]]
        total, assignment = hungarian_algorithm(cost)
        self.assertEqual(total, 42)
        self.assertEqual(assignment, [0])

    def test_valid_assignment_large(self):
        matrix = generate_cost_matrix(60)
        total, assignment = hungarian_algorithm(matrix)
        # Each employee assigned to exactly one unique task
        self.assertEqual(len(assignment), 60)
        self.assertEqual(len(set(assignment)), 60)
        # Verify total cost matches sum of individual costs
        computed = sum(matrix[i][assignment[i]] for i in range(60))
        self.assertEqual(total, computed)

    def test_optimality_vs_brute_force_small(self):
        """For a small matrix, verify Hungarian gives the true minimum via brute force."""
        from itertools import permutations
        cost = [
            [10, 5, 13, 15],
            [3, 9, 18, 3],
            [13, 7, 4, 15],
            [12, 11, 14, 8],
        ]
        h_total, _ = hungarian_algorithm(cost)

        # Brute force: try all permutations
        min_cost = float('inf')
        for perm in permutations(range(4)):
            c = sum(cost[i][perm[i]] for i in range(4))
            min_cost = min(min_cost, c)

        self.assertEqual(h_total, min_cost)


class TestGreedyAlgorithm(unittest.TestCase):
    """Tests for the Greedy algorithm."""

    def test_small_case(self):
        cost = [
            [9, 2, 7],
            [6, 4, 3],
            [5, 8, 1],
        ]
        total, assignment = greedy_algorithm(cost)
        # Greedy picks lowest costs first: (2,2)->1, then (0,1)->2, then (1,0)->6 = 9
        self.assertEqual(len(assignment), 3)
        self.assertEqual(len(set(assignment)), 3)
        computed = sum(cost[i][assignment[i]] for i in range(3))
        self.assertEqual(total, computed)

    def test_valid_assignment_large(self):
        matrix = generate_cost_matrix(70)
        total, assignment = greedy_algorithm(matrix)
        self.assertEqual(len(assignment), 70)
        self.assertEqual(len(set(assignment)), 70)
        computed = sum(matrix[i][assignment[i]] for i in range(70))
        self.assertEqual(total, computed)

    def test_greedy_cost_gte_optimal(self):
        """Greedy cost should be >= Hungarian (optimal) cost."""
        matrix = generate_cost_matrix(50)
        h_total, _ = hungarian_algorithm(matrix)
        g_total, _ = greedy_algorithm(matrix)
        self.assertGreaterEqual(g_total, h_total)

    def test_single_element(self):
        cost = [[99]]
        total, assignment = greedy_algorithm(cost)
        self.assertEqual(total, 99)
        self.assertEqual(assignment, [0])


class TestGenerateChoices(unittest.TestCase):
    """Tests for the answer choice generator."""

    def test_correct_answer_in_choices(self):
        for _ in range(20):
            choices = generate_choices(5000)
            self.assertIn(5000, choices)
            self.assertEqual(len(choices), 3)

    def test_all_choices_different(self):
        for _ in range(20):
            choices = generate_choices(3000)
            self.assertEqual(len(set(choices)), 3)

    def test_only_one_correct(self):
        for _ in range(20):
            choices = generate_choices(8000)
            self.assertEqual(choices.count(8000), 1)

    def test_wrong_answers_are_close(self):
        """Wrong answers should be reasonably close to the correct one."""
        correct = 10000
        for _ in range(50):
            choices = generate_choices(correct)
            for val in choices:
                if val != correct:
                    # Should be within ~20% for normal cases
                    self.assertGreater(val, correct * 0.5)
                    self.assertLess(val, correct * 2.0)


class TestRunRound(unittest.TestCase):
    """Tests for the run_round wrapper function."""

    def test_round_structure(self):
        result = run_round(50)
        self.assertIn("n", result)
        self.assertIn("cost_matrix", result)
        self.assertIn("hungarian", result)
        self.assertIn("greedy", result)
        self.assertEqual(result["n"], 50)

    def test_round_has_timing(self):
        result = run_round(50)
        self.assertIn("time_ms", result["hungarian"])
        self.assertIn("time_ms", result["greedy"])
        self.assertGreaterEqual(result["hungarian"]["time_ms"], 0)
        self.assertGreaterEqual(result["greedy"]["time_ms"], 0)

    def test_round_assignments_valid(self):
        result = run_round(55)
        for algo in ["hungarian", "greedy"]:
            asgn = result[algo]["assignment"]
            self.assertEqual(len(asgn), 55)
            self.assertEqual(len(set(asgn)), 55)


class TestDatabaseOperations(unittest.TestCase):
    """Tests for database save and retrieval."""

    def setUp(self):
        # Use a temporary test database
        import database.connection as conn_module
        self._orig_path = conn_module.DB_PATH
        conn_module.DB_PATH = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "test_pdsa.db"
        )
        from database.mincost import create_tables
        create_tables()

    def tearDown(self):
        import database.connection as conn_module
        test_db = conn_module.DB_PATH
        conn_module.DB_PATH = self._orig_path
        if os.path.exists(test_db):
            os.remove(test_db)
        # Clean up WAL/SHM files
        for ext in ["-wal", "-shm"]:
            path = test_db + ext
            if os.path.exists(path):
                os.remove(path)

    def test_save_and_retrieve(self):
        from database.mincost import save_round, get_all_rounds
        save_round("game-001", "Alice", 1, 50, 1500.0, 1500.0,
                   1500.0, 12.5, 1800.0, 2.3, "CORRECT")
        rows = get_all_rounds()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "game-001")  # game_id
        self.assertEqual(rows[0][1], "Alice")      # player_name
        self.assertEqual(rows[0][2], 1)             # round_number
        self.assertEqual(rows[0][3], 50)            # n_value

    def test_multiple_rounds(self):
        from database.mincost import save_round, get_all_rounds
        save_round("game-002", "Bob", 1, 60, 2000.0, 2000.0,
                   2000.0, 15.0, 2500.0, 3.0, "CORRECT")
        save_round("game-002", "Bob", 2, 75, 3000.0, 3200.0,
                   3200.0, 20.0, 3500.0, 4.0, "WRONG")
        rows = get_all_rounds()
        self.assertEqual(len(rows), 2)

    def test_update_overall_result(self):
        from database.mincost import save_round, update_overall_result, get_all_rounds
        save_round("game-003", "Charlie", 1, 55, 1000.0, 1000.0,
                   1000.0, 10.0, 1200.0, 2.0, "CORRECT")
        update_overall_result("game-003", "WIN")
        rows = get_all_rounds()
        # overall_result is index 11 in the SELECT
        self.assertEqual(rows[0][11], "WIN")

    def test_overall_result_null_before_update(self):
        from database.mincost import save_round, get_all_rounds
        save_round("game-004", "Dave", 1, 50, 900.0, 1000.0,
                   1000.0, 8.0, 1100.0, 1.5, "WRONG")
        rows = get_all_rounds()
        self.assertIsNone(rows[0][11])  # overall_result should be NULL


if __name__ == "__main__":
    unittest.main()
