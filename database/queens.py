# DB tables for Sixteen Queens game
import sqlite3
import time


class DatabaseManager:
    def __init__(self, db_name="chess_game.db"):
        self.db_name = db_name
        self.init_db()

    # ✅ Safe connection (prevents locking issues)
    def connect(self):
        return sqlite3.connect(self.db_name, timeout=10, check_same_thread=False)

    def init_db(self):
        conn = self.connect()
        cursor = conn.cursor()

        # ✅ Enable WAL mode (important for concurrency)
        cursor.execute("PRAGMA journal_mode=WAL;")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Player_Responses (
                name TEXT,
                answer TEXT UNIQUE
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Solutions (
                solution TEXT UNIQUE
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Program_Respond (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequential INTEGER,
                threaded INTEGER,
                time_taken_seq REAL,
                time_taken_thread REAL
            )
        """
        )

        conn.commit()
        conn.close()

    # ---------- PLAYER ----------
    def save_player_response(self, name, answer):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Player_Responses VALUES (?, ?)", (name, answer))
        conn.commit()
        conn.close()

    def get_player_solution_count(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Player_Responses")
        result = cursor.fetchone()[0]
        conn.close()
        return result

    def clear_player_responses(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Player_Responses")
        conn.commit()
        conn.close()

    # ---------- PERFORMANCE ----------
    def save_performance_stats(self, s_count, t_count, s_time, t_time):
        for _ in range(5):  # retry logic
            try:
                conn = self.connect()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Program_Respond (sequential, threaded, time_taken_seq, time_taken_thread) VALUES (?,?,?,?)",
                    (s_count, t_count, s_time, t_time),
                )
                conn.commit()
                conn.close()
                return
            except sqlite3.OperationalError:
                time.sleep(0.1)

    # ---------- SOLUTIONS (BULK INSERT - FIXES LOCK ERROR) ----------
    def save_solutions_bulk(self, solutions):
        for _ in range(5):  # retry if locked
            try:
                conn = self.connect()
                cursor = conn.cursor()

                cursor.executemany(
                    "INSERT OR IGNORE INTO Solutions VALUES (?)",
                    [(s,) for s in solutions],
                )

                conn.commit()
                conn.close()
                return
            except sqlite3.OperationalError:
                time.sleep(0.1)
