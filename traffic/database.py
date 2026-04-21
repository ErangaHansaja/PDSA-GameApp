import sqlite3
import json
import os
from datetime import datetime


def init_db(db_path=None):
    """Initialize the database and create the game_results table if it doesn't exist."""
    # Use absolute path to ensure database is always accessible
    if db_path is None:
        # Get the directory of the current file (traffic folder)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "game_results.db")
    
    # Ensure the directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            round_number INTEGER NOT NULL,
            capacities TEXT NOT NULL,
            player_answer INTEGER NOT NULL,
            correct_max_flow INTEGER NOT NULL,
            result TEXT NOT NULL,
            algorithm_1_time REAL,
            algorithm_2_time REAL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    print(f"[DATABASE] Initialized at: {db_path}")
    return conn


def save_result(conn, player_name, round_number, capacities, player_answer, 
                correct_max_flow, result, algo1_time, algo2_time):
    """Save game result to the database."""
    try:
        cursor = conn.cursor()
        
        # Convert tuple keys to strings for JSON serialization
        # Example: {('A', 'B'): 10} -> {"A->B": 10}
        capacities_str = {}
        for (from_node, to_node), capacity in capacities.items():
            capacities_str[f"{from_node}->{to_node}"] = capacity
        
        cursor.execute('''
            INSERT INTO game_results 
            (player_name, round_number, capacities, player_answer, correct_max_flow, 
             result, algorithm_1_time, algorithm_2_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_name,
            round_number,
            json.dumps(capacities_str),
            player_answer,
            correct_max_flow,
            result,
            algo1_time,
            algo2_time,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print(f"[DATABASE] Successfully saved result for {player_name}, round {round_number}")
        return True
    except Exception as e:
        print(f"[DATABASE ERROR] Failed to save result: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_player_history(conn, player_name):
    """Retrieve all game results for a specific player."""
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM game_results 
        WHERE player_name = ? 
        ORDER BY created_at DESC
    ''', (player_name,))
    
    return cursor.fetchall()


def get_all_results(conn):
    """Retrieve all game results for all players (most recent first)."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, player_name, round_number, capacities, player_answer, correct_max_flow,
               result, algorithm_1_time, algorithm_2_time, created_at
        FROM game_results
        ORDER BY created_at DESC
        """
    )
    return cursor.fetchall()
