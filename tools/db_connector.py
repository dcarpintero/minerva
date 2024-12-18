import hashlib
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
        query = """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            summary TEXT,
            is_scam BOOLEAN NOT NULL,
            confidence_level INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_hash TEXT UNIQUE NOT NULL
        )
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query)

    def _compute_hash(self, text: str) -> str:
        """Compute SHA-256 hash of the input text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def store_result(
        self,
        text: str,
        summary: Optional[str],
        is_scam: bool,
        confidence_level: int
    ) -> Optional[int]:  # Updated return type hint
        """Store analysis result in the database.
        """
        message_hash = self._compute_hash(text)
        hash_query = "SELECT id FROM results WHERE message_hash = ?"

        query = """
        INSERT INTO results (text, summary, is_scam, confidence_level, message_hash)
        VALUES (?, ?, ?, ?, ?)
        """
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(hash_query, (message_hash,))
            existing_id = cursor.fetchone()
            
            if existing_id:
                return None
            
            cursor = conn.execute(
                query,
                (text, summary, is_scam, confidence_level, message_hash)
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

    def get_all(self) -> pd.DataFrame:
        """Retrieve all analysis results as a DataFrame.
        """
        query = "SELECT * FROM results"
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
            return df
                