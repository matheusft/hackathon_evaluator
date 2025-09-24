"""
Leaderboard Management Module
============================

Manages the hackathon leaderboard stored in PostgreSQL database.
"""

import os
from typing import List, Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor


class LeaderboardManager:
    """Manages leaderboard operations for the hackathon."""

    def __init__(self):
        """Initialize leaderboard manager."""
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        # Defer database connection until first use
        self._table_initialized = False

    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.database_url)

    def _ensure_table_exists(self) -> None:
        """Ensure the leaderboard table exists."""
        if self._table_initialized:
            return
            
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS leaderboard (
                        id SERIAL PRIMARY KEY,
                        participant_name VARCHAR(255) NOT NULL,
                        submission_tag VARCHAR(100) NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        score FLOAT NOT NULL,
                        UNIQUE(participant_name, submission_tag)
                    )
                """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_leaderboard_score 
                    ON leaderboard(score DESC)
                """
                )
                conn.commit()
                self._table_initialized = True
        except Exception:
            # Don't raise here - let individual methods handle connection failures
            pass

    def update_leaderboard(
        self, participant_name: str, submission_tag: str, score: float
    ) -> None:
        """
        Update leaderboard with new submission.

        Args:
            participant_name: Name of the participant/team
            submission_tag: Tag for this submission (e.g., v1.0)
            score: Score achieved by the submission
        """
        self._ensure_table_exists()
        
        timestamp = datetime.now()
        score_float = float(score)

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO leaderboard 
                        (participant_name, submission_tag, timestamp, score)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (participant_name, submission_tag) 
                    DO UPDATE SET 
                        score = EXCLUDED.score,
                        timestamp = EXCLUDED.timestamp
                    """,
                    (participant_name, submission_tag, timestamp, score_float),
                )
                conn.commit()

    def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get current leaderboard sorted by score.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of leaderboard entries with rankings
        """
        self._ensure_table_exists()
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT 
                        participant_name,
                        submission_tag,
                        timestamp,
                        score,
                        RANK() OVER (ORDER BY score DESC) as rank
                    FROM leaderboard
                    ORDER BY score DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                results = cur.fetchall()

                return [
                    {
                        "participant_name": row["participant_name"],
                        "submission_tag": row["submission_tag"],
                        "timestamp": row["timestamp"].isoformat(),
                        "score": float(row["score"]),
                        "rank": int(row["rank"]),
                        "formatted_score": f"{float(row['score']):.3f}",
                    }
                    for row in results
                ]

    def get_participant_rank(self, participant_name: str) -> int:
        """
        Get the rank of a specific participant.

        Args:
            participant_name: Name of the participant

        Returns:
            Rank of the participant (1-indexed), or 0 if not found
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    WITH ranked_leaderboard AS (
                        SELECT 
                            participant_name,
                            RANK() OVER (ORDER BY score DESC) as rank
                        FROM leaderboard
                    )
                    SELECT rank FROM ranked_leaderboard
                    WHERE participant_name = %s
                    LIMIT 1
                    """,
                    (participant_name,),
                )
                result = cur.fetchone()
                return int(result[0]) if result else 0
