# DB tables for Minimum Cost game
from database.connection import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Check if old schema exists (missing game_id column) and migrate
    cursor.execute("PRAGMA table_info(mincost_rounds)")
    cols = [row[1] for row in cursor.fetchall()]
    if cols and "game_id" not in cols:
        cursor.execute("DROP TABLE mincost_rounds")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mincost_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            round_number INTEGER NOT NULL,
            n_value INTEGER NOT NULL,
            player_guess REAL NOT NULL,
            correct_answer REAL NOT NULL,
            hungarian_answer REAL NOT NULL,
            hungarian_time REAL NOT NULL,
            greedy_answer REAL NOT NULL,
            greedy_time REAL NOT NULL,
            round_result TEXT NOT NULL,
            overall_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_round(game_id, player_name, round_number, n_value, player_guess,
               correct_answer, hungarian_answer, hungarian_time,
               greedy_answer, greedy_time, round_result):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mincost_rounds
        (game_id, player_name, round_number, n_value, player_guess,
         correct_answer, hungarian_answer, hungarian_time,
         greedy_answer, greedy_time, round_result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (game_id, player_name, round_number, n_value, player_guess,
          correct_answer, hungarian_answer, hungarian_time,
          greedy_answer, greedy_time, round_result))
    conn.commit()
    conn.close()


def update_overall_result(game_id, overall_result):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE mincost_rounds SET overall_result = ? WHERE game_id = ?
    """, (overall_result, game_id))
    conn.commit()
    conn.close()


def get_all_rounds():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT game_id, player_name, round_number, n_value, player_guess,
               correct_answer, hungarian_answer, hungarian_time,
               greedy_answer, greedy_time, round_result, overall_result,
               created_at
        FROM mincost_rounds
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_scoreboard():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            player_name,
            SUM(CASE WHEN round_result = 'CORRECT' THEN 1 ELSE 0 END) AS wins,
            COUNT(*) AS total_rounds,
            ROUND(
                SUM(CASE WHEN round_result = 'CORRECT' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                1
            ) AS win_pct,
            DATE(MIN(created_at)) AS played_at
        FROM mincost_rounds
        GROUP BY game_id
        ORDER BY wins DESC, win_pct DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
