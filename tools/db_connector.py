import pandas as pd
import sqlite3

from typing import Optional
from datetime import datetime

class DatabaseConnector:
    """Manages database operations for storing analysis results."""

    def __init__(self, db_path: str = "sqlite3/results.db"):
        """Initialize database connection and create table if it doesn't exist.
        """
        self.db_path = db_path
        self._create_table()

    def _create_table(self) -> None:
        """Create results table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            summary TEXT,
            is_scam BOOLEAN NOT NULL,
            confidence_level INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query)

    def store_result(
        self,
        text: str,
        summary: Optional[str],
        is_scam: bool,
        confidence_level: int
    ) -> int:
        """Store analysis result in the database.
        """
        query = """
        INSERT INTO results (text, summary, is_scam, confidence_level)
        VALUES (?, ?, ?, ?)
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                query,
                (text, summary, is_scam, confidence_level)
            )
            return cursor.lastrowid

    def get_result(self, result_id: int) -> Optional[dict]:
        """Retrieve a specific analysis result by ID.
        """
        query = "SELECT * FROM results WHERE id = ?"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (result_id,))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            return None

    def get_top_k(self, k: int = 10) -> pd.DataFrame:
        """Retrieve most recent analysis results as a DataFrame.
        """
        query = "SELECT * FROM results ORDER BY created_at DESC LIMIT ?"
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=(k,))
            return df
                