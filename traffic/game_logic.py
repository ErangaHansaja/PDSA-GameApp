from graph_generator import generate_capacities
from max_flow_solver import ford_fulkerson, edmonds_karp


class Game:
    """Manages game state and logic for the Maximum Flow game."""
    
    def __init__(self):
        """Initialize a new game instance."""
        self.round_number = 0
        self.capacities = None
        self.correct_max_flow = None
        self.algo1_time = None
        self.algo2_time = None
        self.player_answer = None
        self.result = None
    
    def start_round(self):
        """
        Start a new round by generating random capacities and calculating the correct answer.
        
        Returns:
            Dictionary of edge capacities
        """
        self.round_number += 1
        
        # Generate random capacities
        self.capacities = generate_capacities()
        
        # Calculate correct answer using both algorithms
        ff_flow, ff_time = ford_fulkerson('A', 'T', self.capacities)
        ek_flow, ek_time = edmonds_karp('A', 'T', self.capacities)
        
        # Both algorithms should produce the same result
        self.correct_max_flow = ff_flow
        self.algo1_time = ff_time
        self.algo2_time = ek_time
        
        # Reset player answer and result
        self.player_answer = None
        self.result = None
        
        return self.capacities
    
    def check_answer(self, player_answer):
        """
        Check if the player's answer is correct.
        
        Args:
            player_answer: Integer answer from the player
        
        Returns:
            String result: 'Win', 'Lose', or 'Draw'
        """
        self.player_answer = int(player_answer)
        
        if self.player_answer == self.correct_max_flow:
            self.result = 'Win'
        elif abs(self.player_answer - self.correct_max_flow) <= 1:
            # Draw if answer is within ±1 of correct answer
            self.result = 'Draw'
        else:
            self.result = 'Lose'
        
        return self.result
    
    def get_result(self):
        """
        Get the current round result.
        
        Returns:
            Dictionary with all round information
        """
        return {
            'round_number': self.round_number,
            'capacities': self.capacities,
            'player_answer': self.player_answer,
            'correct_max_flow': self.correct_max_flow,
            'result': self.result,
            'algo1_time': self.algo1_time,
            'algo2_time': self.algo2_time
        }
    
    def get_capacities(self):
        """Get current round capacities."""
        return self.capacities
    
    def get_correct_answer(self):
        """Get the correct maximum flow value."""
        return self.correct_max_flow
