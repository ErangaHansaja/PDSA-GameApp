import sqlite3
import tkinter as tk
from tkinter import messagebox

DB_FILE = "knights_tour.db"


def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS winners (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                board_size INTEGER NOT NULL,
                start_pos  TEXT    NOT NULL,
                moves      INTEGER NOT NULL,
                sequence   TEXT    NOT NULL,
                round      TEXT    NOT NULL,
                time_used  INTEGER NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS algorithm_times (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name     TEXT    NOT NULL,
                round_number    INTEGER NOT NULL,
                algorithm_type  TEXT    NOT NULL,
                board_size      INTEGER NOT NULL,
                time_taken_ms   REAL    NOT NULL,
                timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {e}")

def save_winner(name: str, board_size: int, start_pos: tuple,
                moves: int, sequence: list, round: str, time_used: int):
    """Insert a winning record into the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO winners (name, board_size, start_pos, moves, sequence, round, time_used) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                name,
                board_size,
                str(start_pos),
                moves,
                str(sequence),
                round,
                time_used
            ),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")


def fetch_winners():
    """Return the 50 most recent winners as a list of tuples."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT name, board_size, start_pos, moves, sequence, round, time_used "
            "FROM winners ORDER BY id DESC LIMIT 50"
        )
        rows = c.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")


def save_algorithm_time(player_name: str, round_number: int, algorithm_type: str, 
                       board_size: int, time_taken_ms: float):
    """Insert an algorithm execution time record into the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO algorithm_times (player_name, round_number, algorithm_type, board_size, time_taken_ms) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                player_name,
                round_number,
                algorithm_type,
                board_size,
                time_taken_ms
            ),
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")


def fetch_algorithm_times(player_name: str = None, limit: int = 100):
    """Fetch algorithm timing records from the database.
    
    Args:
        player_name: If provided, fetch only records for this player
        limit: Maximum number of records to return
    
    Returns:
        List of tuples: (player_name, round_number, algorithm_type, board_size, time_taken_ms, timestamp)
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if player_name:
            c.execute(
                "SELECT player_name, round_number, algorithm_type, board_size, time_taken_ms, timestamp "
                "FROM algorithm_times WHERE player_name = ? ORDER BY id DESC LIMIT ?",
                (player_name, limit)
            )
        else:
            c.execute(
                "SELECT player_name, round_number, algorithm_type, board_size, time_taken_ms, timestamp "
                "FROM algorithm_times ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        rows = c.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")


def get_algorithm_stats(player_name: str = None):
    """Get average execution times by algorithm and board size.
    
    Args:
        player_name: If provided, calculate stats only for this player
        
    Returns:
        Dictionary with statistics organized by algorithm and board size
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if player_name:
            c.execute(
                "SELECT algorithm_type, board_size, AVG(time_taken_ms) as avg_time, COUNT(*) as count "
                "FROM algorithm_times WHERE player_name = ? GROUP BY algorithm_type, board_size",
                (player_name,)
            )
        else:
            c.execute(
                "SELECT algorithm_type, board_size, AVG(time_taken_ms) as avg_time, COUNT(*) as count "
                "FROM algorithm_times GROUP BY algorithm_type, board_size"
            )
        rows = c.fetchall()
        conn.close()
        
        stats = {}
        for algo_type, board_size, avg_time, count in rows:
            key = f"{algo_type} ({board_size}×{board_size})"
            stats[key] = {"avg_time_ms": avg_time, "count": count}
        return stats
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")
