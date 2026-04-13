# DB tables for Minimum Cost game
from database.connection import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mincost_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_number INTEGER NOT NULL,
            n_size INTEGER NOT NULL,
            hungarian_cost REAL NOT NULL,
            hungarian_time_ms REAL NOT NULL,
            greedy_cost REAL NOT NULL,
            greedy_time_ms REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_round(round_number, n_size, hungarian_cost, hungarian_time_ms,
               greedy_cost, greedy_time_ms):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mincost_rounds
        (round_number, n_size, hungarian_cost, hungarian_time_ms, greedy_cost, greedy_time_ms)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (round_number, n_size, hungarian_cost, hungarian_time_ms,
          greedy_cost, greedy_time_ms))
    conn.commit()
    conn.close()


def get_all_rounds():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT round_number, n_size, hungarian_cost, hungarian_time_ms,
               greedy_cost, greedy_time_ms, created_at
        FROM mincost_rounds
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
