import sqlite3


class DatabaseManager:
    def __init__(self, db_name="chess_game.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

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

    def save_player_response(self, name, answer):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Player_Responses VALUES (?, ?)", (name, answer))
        conn.commit()
        conn.close()

    def save_solution(self, solution):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Solutions VALUES (?)", (solution,))
        conn.commit()
        conn.close()

    def save_performance_stats(self, s_count, t_count, s_time, t_time):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Program_Respond (sequential, threaded, time_taken_seq, time_taken_thread) VALUES (?,?,?,?)",
            (s_count, t_count, s_time, t_time),
        )
        conn.commit()
        conn.close()

    def get_player_solution_count(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Player_Responses")
        result = cursor.fetchone()[0]
        conn.close()
        return result

    def clear_player_responses(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Player_Responses")
        conn.commit()
        conn.close()
