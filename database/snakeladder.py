# DB tables for Snake and Ladder game
from database.connection import get_connection

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS winners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        answer INTEGER,
        board_size INTEGER,
        bfs_time REAL,
        dijkstra_time REAL
    )
    """)
    conn.commit()
    conn.close()

def save_winner(name, answer, board_size, bfs_t, dijk_t):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO winners (name, answer, board_size, bfs_time, dijkstra_time) VALUES (?, ?, ?, ?, ?)",
        (name, answer, board_size, bfs_t, dijk_t)
    )
    conn.commit()
    conn.close()