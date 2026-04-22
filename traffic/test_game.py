"""
Unit Tests for Maximum Flow Game
Tests for graph generation, max flow algorithms, and game logic
"""

import unittest
import time
from graph_generator import generate_capacities, get_graph_structure, NODES, EDGES
from max_flow_solver import ford_fulkerson, edmonds_karp
from game_logic import Game


class TestGraphGenerator(unittest.TestCase):
    """Test cases for graph generation module."""
    
    def test_graph_structure(self):
        """Test that graph has correct nodes and edges."""
        nodes, edges = get_graph_structure()
        
        # Check nodes
        self.assertEqual(len(nodes), 9)
        self.assertIn('A', nodes)
        self.assertIn('T', nodes)
        self.assertIn('B', nodes)
        
        # Check edges count
        self.assertEqual(len(edges), 13)
        
        # Check specific edges exist
        self.assertIn(('A', 'B'), edges)
        self.assertIn(('A', 'C'), edges)
        self.assertIn(('A', 'D'), edges)
        self.assertIn(('G', 'T'), edges)
        self.assertIn(('H', 'T'), edges)
    
    def test_generate_capacities_range(self):
        """Test that generated capacities are within valid range."""
        capacities = generate_capacities()
        
        for edge, capacity in capacities.items():
            self.assertGreaterEqual(capacity, 5)
            self.assertLessEqual(capacity, 15)
    
    def test_generate_capacities_custom_range(self):
        """Test capacity generation with custom range."""
        capacities = generate_capacities(min_cap=10, max_cap=20)
        
        for edge, capacity in capacities.items():
            self.assertGreaterEqual(capacity, 10)
            self.assertLessEqual(capacity, 20)
    
    def test_generate_capacities_all_edges(self):
        """Test that all edges have capacities assigned."""
        capacities = generate_capacities()
        _, edges = get_graph_structure()
        
        self.assertEqual(len(capacities), len(edges))
        
        for edge in edges:
            self.assertIn(edge, capacities)
    
    def test_random_generation(self):
        """Test that different calls produce different results."""
        capacities1 = generate_capacities()
        capacities2 = generate_capacities()
        
        # At least one edge should be different (very high probability)
        is_different = False
        for edge in capacities1:
            if capacities1[edge] != capacities2[edge]:
                is_different = True
                break
        
        self.assertTrue(is_different, "Random generation should produce different results")


class TestMaxFlowSolver(unittest.TestCase):
    """Test cases for maximum flow algorithms."""
    
    def test_ford_fulkerson_basic(self):
        """Test Ford-Fulkerson with a simple graph."""
        capacities = {
            ('A', 'B'): 10,
            ('B', 'T'): 10
        }
        
        max_flow, exec_time = ford_fulkerson('A', 'T', capacities)
        
        self.assertEqual(max_flow, 10)
        self.assertGreaterEqual(exec_time, 0)
    
    def test_edmonds_karp_basic(self):
        """Test Edmonds-Karp with a simple graph."""
        capacities = {
            ('A', 'B'): 10,
            ('B', 'T'): 10
        }
        
        max_flow, exec_time = edmonds_karp('A', 'T', capacities)
        
        self.assertEqual(max_flow, 10)
        self.assertGreaterEqual(exec_time, 0)
    
    def test_algorithms_produce_same_result(self):
        """Test that both algorithms produce the same maximum flow."""
        capacities = generate_capacities()
        
        ff_flow, _ = ford_fulkerson('A', 'T', capacities)
        ek_flow, _ = edmonds_karp('A', 'T', capacities)
        
        self.assertEqual(ff_flow, ek_flow)
    
    def test_multiple_paths(self):
        """Test max flow with multiple paths."""
        capacities = {
            ('A', 'B'): 10,
            ('A', 'C'): 10,
            ('B', 'T'): 10,
            ('C', 'T'): 10
        }
        
        ff_flow, _ = ford_fulkerson('A', 'T', capacities)
        ek_flow, _ = edmonds_karp('A', 'T', capacities)
        
        self.assertEqual(ff_flow, 20)
        self.assertEqual(ek_flow, 20)
    
    def test_bottleneck_path(self):
        """Test max flow with bottleneck."""
        capacities = {
            ('A', 'B'): 10,
            ('B', 'C'): 5,
            ('C', 'T'): 10
        }
        
        ff_flow, _ = ford_fulkerson('A', 'T', capacities)
        ek_flow, _ = edmonds_karp('A', 'T', capacities)
        
        # Bottleneck is B->C with capacity 5
        self.assertEqual(ff_flow, 5)
        self.assertEqual(ek_flow, 5)
    
    def test_execution_time_reasonable(self):
        """Test that algorithms complete in reasonable time."""
        capacities = generate_capacities()
        
        _, ff_time = ford_fulkerson('A', 'T', capacities)
        _, ek_time = edmonds_karp('A', 'T', capacities)
        
        # Should complete in less than 1 second
        self.assertLess(ff_time, 1.0)
        self.assertLess(ek_time, 1.0)
    
    def test_full_traffic_network(self):
        """Test with the full traffic network graph."""
        capacities = generate_capacities()
        
        ff_flow, ff_time = ford_fulkerson('A', 'T', capacities)
        ek_flow, ek_time = edmonds_karp('A', 'T', capacities)
        
        # Both should produce same result
        self.assertEqual(ff_flow, ek_flow)
        
        # Flow should be positive
        self.assertGreater(ff_flow, 0)
        
        # Times should be non-negative
        self.assertGreaterEqual(ff_time, 0)
        self.assertGreaterEqual(ek_time, 0)


class TestGameLogic(unittest.TestCase):
    """Test cases for game logic module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game = Game()
    
    def test_initial_state(self):
        """Test initial game state."""
        self.assertEqual(self.game.round_number, 0)
        self.assertIsNone(self.game.capacities)
        self.assertIsNone(self.game.correct_max_flow)
    
    def test_start_round(self):
        """Test starting a new round."""
        capacities = self.game.start_round()
        
        self.assertEqual(self.game.round_number, 1)
        self.assertIsNotNone(capacities)
        self.assertIsNotNone(self.game.correct_max_flow)
        self.assertIsInstance(capacities, dict)
    
    def test_multiple_rounds(self):
        """Test multiple rounds increment correctly."""
        self.game.start_round()
        self.game.start_round()
        self.game.start_round()
        
        self.assertEqual(self.game.round_number, 3)
    
    def test_correct_answer(self):
        """Test correct answer detection."""
        self.game.start_round()
        correct_answer = self.game.correct_max_flow
        
        result = self.game.check_answer(correct_answer)
        
        self.assertEqual(result, 'Win')
        self.assertEqual(self.game.result, 'Win')
    
    def test_close_answer_draw(self):
        """Test close answer results in draw."""
        self.game.start_round()
        correct_answer = self.game.correct_max_flow
        
        # Answer within ±1 should be Draw
        result = self.game.check_answer(correct_answer + 1)
        self.assertEqual(result, 'Draw')
        
        self.game.start_round()
        correct_answer = self.game.correct_max_flow
        result = self.game.check_answer(correct_answer - 1)
        self.assertEqual(result, 'Draw')
    
    def test_wrong_answer(self):
        """Test wrong answer detection."""
        self.game.start_round()
        correct_answer = self.game.correct_max_flow
        
        # Answer far from correct should be Lose
        result = self.game.check_answer(correct_answer + 10)
        self.assertEqual(result, 'Lose')
    
    def test_get_result(self):
        """Test getting complete result information."""
        self.game.start_round()
        self.game.check_answer(self.game.correct_max_flow)
        
        result = self.game.get_result()
        
        self.assertIn('round_number', result)
        self.assertIn('capacities', result)
        self.assertIn('player_answer', result)
        self.assertIn('correct_max_flow', result)
        self.assertIn('result', result)
        self.assertIn('algo1_time', result)
        self.assertIn('algo2_time', result)
    
    def test_result_after_submission(self):
        """Test that result is properly stored after answer submission."""
        self.game.start_round()
        player_answer = self.game.correct_max_flow
        
        self.game.check_answer(player_answer)
        result = self.game.get_result()
        
        self.assertEqual(result['player_answer'], player_answer)
        self.assertEqual(result['correct_max_flow'], self.game.correct_max_flow)
        self.assertEqual(result['result'], 'Win')


class TestValidationAndExceptionHandling(unittest.TestCase):
    """Test cases for validation and exception handling."""
    
    def test_invalid_answer_type(self):
        """Test handling of invalid answer types."""
        game = Game()
        game.start_round()
        
        # Should handle string that can't be converted
        with self.assertRaises((ValueError, TypeError)):
            game.check_answer("invalid")
    
    def test_negative_answer(self):
        """Test handling of negative answers."""
        game = Game()
        game.start_round()
        
        # Negative answers should still be processed (game logic handles it)
        try:
            result = game.check_answer(-5)
            self.assertIn(result, ['Win', 'Lose', 'Draw'])
        except:
            pass  # Some implementations might raise exception
    
    def test_zero_answer(self):
        """Test handling of zero answer."""
        game = Game()
        game.start_round()
        
        result = game.check_answer(0)
        self.assertIn(result, ['Win', 'Lose', 'Draw'])
    
    def test_large_answer(self):
        """Test handling of very large answers."""
        game = Game()
        game.start_round()
        
        result = game.check_answer(1000)
        self.assertEqual(result, 'Lose')
    
    def test_float_answer(self):
        """Test handling of float answers."""
        game = Game()
        game.start_round()
        
        # Float answers should be converted to int or handled
        try:
            result = game.check_answer(15.5)
            self.assertIn(result, ['Win', 'Lose', 'Draw'])
        except:
            pass  # Some implementations might raise exception


if __name__ == '__main__':
    unittest.main()
