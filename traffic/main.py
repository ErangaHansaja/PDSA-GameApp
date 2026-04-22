import tkinter as tk
from tkinter import messagebox
from database.traffic import init_db, save_result, get_player_history, get_all_results
from game_logic import Game
from ui.start_screen import StartScreen
from ui.game_screen import GameScreen
from ui.result_screen import ResultScreen
from ui.statistics_screen import StatisticsScreen


class MaximumFlowGame:
    """Main application class for the Maximum Flow Game."""
    
    def __init__(self):
        """Initialize the application."""
        # Create main window
        self.root = tk.Tk()
        self.root.title("Traffic Simulation Problem - Maximum Flow Game")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        
        # Initialize database
        self.db_conn = init_db()
        
        # Initialize game logic
        self.game = Game()
        
        # Player info
        self.player_name = None
        
        # Current screen
        self.current_screen = None
        
        # Start with the start screen
        self.show_start_screen()
    
    def show_start_screen(self):
        """Show the start screen."""
        self.clear_screen()
        self.current_screen = StartScreen(
            self.root,
            on_start=self.handle_game_start,
            on_statistics=self.show_statistics_screen,
            on_back_to_dashboard=self.handle_back_to_dashboard,
        )

    def show_statistics_screen(self):
        """Show the statistics page with all database results."""
        self.clear_screen()
        self.current_screen = StatisticsScreen(
            self.root,
            on_back=self.show_start_screen,
        )
        rows = get_all_results(self.db_conn)
        self.current_screen.load_rows(rows)
    
    def show_game_screen(self):
        """Show the game screen with a new round."""
        self.clear_screen()
        
        # Start a new round
        capacities = self.game.start_round()
        
        self.current_screen = GameScreen(
            self.root,
            on_submit=self.handle_answer_submit,
            round_number=self.game.round_number,
            on_back_to_dashboard=self.handle_back_to_dashboard,
        )
        
        # Draw the graph
        self.current_screen.draw_graph(capacities)
        
        # Update stats panel
        self.update_game_stats()
        
        # Show algorithm results (correct answer)
        self.current_screen.update_algorithm_results(
            correct_answer=self.game.correct_max_flow,
            algo1_time=self.game.algo1_time,
            algo2_time=self.game.algo2_time
        )
    
    def show_result_screen(self):
        """Show the result screen."""
        self.clear_screen()
        
        self.current_screen = ResultScreen(
            self.root,
            on_play_again=self.handle_play_again,
            on_main_menu=self.handle_main_menu
        )
        
        # Display results
        game_result = self.game.get_result()
        self.current_screen.show_result(game_result)
    
    def clear_screen(self):
        """Clear the current screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None
    
    def update_game_stats(self):
        """Update the game stats panel with player history."""
        if not hasattr(self.current_screen, 'update_stats'):
            return
        
        try:
            # Get player history from database
            history = get_player_history(self.db_conn, self.player_name)
            
            if history and len(history) > 0:
                # Get last game result
                last_game = history[0]
                # history format: (id, player_name, round_number, capacities, 
                #                  player_answer, correct_max_flow, result, 
                #                  algorithm_1_time, algorithm_2_time, created_at)
                
                last_winner = self.player_name if last_game[6] == 'Win' else 'N/A'
                last_answer = last_game[5]  # correct_max_flow
                
                # Calculate average time
                total_time = 0
                count = 0
                for game in history:
                    if game[7] and game[8]:  # algorithm_1_time and algorithm_2_time
                        total_time += (game[7] + game[8]) / 2
                        count += 1
                
                avg_time = total_time / count if count > 0 else None
                
                # Update the stats panel
                self.current_screen.update_stats(
                    last_winner=last_winner,
                    last_answer=last_answer,
                    avg_time=avg_time
                )
            else:
                # First game - show defaults
                self.current_screen.update_stats()
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def handle_game_start(self, player_name):
        """
        Handle game start from the start screen.
        
        Args:
            player_name: Player's name
        """
        try:
            print(f"handle_game_start called with: {player_name}")  # Debug
            self.player_name = player_name
            self.show_game_screen()
        except Exception as e:
            print(f"Error in handle_game_start: {e}")
            import traceback
            traceback.print_exc()
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to start game:\n{str(e)}")
    
    def handle_answer_submit(self, answer):
        """
        Handle answer submission from the game screen.
        
        Args:
            answer: Player's answer (integer)
        """
        try:
            print(f"handle_answer_submit called with: {answer}")  # Debug
            # Check the answer
            result = self.game.check_answer(answer)
            
            # Get game result details
            game_result = self.game.get_result()
            correct_answer = game_result['correct_max_flow']
            
            # Show feedback message
            if result == 'Win':
                messagebox.showinfo(
                    "Correct! 🎉",
                    f"Your answer: {answer}\n"
                    f"Correct answer: {correct_answer}\n\n"
                    f"Excellent! You got it right!"
                )
            elif result == 'Draw':
                messagebox.showinfo(
                    "Close! 🤝",
                    f"Your answer: {answer}\n"
                    f"Correct answer: {correct_answer}\n\n"
                    f"So close! Within ±1 of the correct answer."
                )
            else:  # Lose
                messagebox.showinfo(
                    "Incorrect ❌",
                    f"Your answer: {answer}\n"
                    f"Correct answer: {correct_answer}\n\n"
                    f"Better luck next time!"
                )
            
            # Save result to database
            save_result(
                self.db_conn,
                self.player_name,
                game_result['round_number'],
                game_result['capacities'],
                game_result['player_answer'],
                game_result['correct_max_flow'],
                game_result['result'],
                game_result['algo1_time'],
                game_result['algo2_time']
            )
            
            print(f"Result: {game_result['result']}")  # Debug
            # Show result screen
            self.show_result_screen()
        except Exception as e:
            print(f"Error in handle_answer_submit: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to submit answer:\n{str(e)}")
    
    def handle_play_again(self):
        """Handle play again button click."""
        self.show_game_screen()
    
    def handle_main_menu(self):
        """Handle back to main menu button click."""
        self.player_name = None
        self.game = Game()  # Reset game
        self.show_start_screen()
    
    def handle_back_to_dashboard(self):
        """
        Return to the dashboard. Replace with real navigation when a dashboard exists.
        """
        pass
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'db_conn'):
            self.db_conn.close()


if __name__ == "__main__":
    app = MaximumFlowGame()
    app.run()
