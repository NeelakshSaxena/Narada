import os
import sqlite3
from datetime import datetime

class TerminalSessionManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            workspace = os.path.expanduser("~/.narada")
            os.makedirs(workspace, exist_ok=True)
            db_path = os.path.join(workspace, "terminal_sessions.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            conn.commit()

    def create_session(self, session_id: str, title: str = "New Session"):
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session_id, title, now, now)
            )
            conn.commit()

    def add_message(self, session_id: str, role: str, content: str):
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Ensure session exists (in case it wasn't explicitly created)
            cursor.execute(
                "INSERT OR IGNORE INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session_id, "Session " + session_id[:6], now, now)
            )
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, now)
            )
            cursor.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (now, session_id)
            )
            conn.commit()

    def get_messages(self, session_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,)
            )
            return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

    def list_sessions(self, limit: int = 10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            )
            return [{"id": row[0], "title": row[1], "updated_at": row[2]} for row in cursor.fetchall()]

    def update_session_title(self, session_id: str, title: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sessions SET title = ? WHERE id = ?",
                (title, session_id)
            )
            conn.commit()
