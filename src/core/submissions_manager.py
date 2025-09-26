"""
User Submissions Management Module
==================================

Manages user submissions data stored in PostgreSQL database.
"""

import os
from typing import Dict, Optional
from datetime import datetime
import psycopg2


class SubmissionsManager:
    """Manages user submissions operations."""

    def __init__(self) -> None:
        """Initialize submissions manager."""
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        self._table_initialized = False

    def _get_connection(self):
        """Get database connection with timeout."""
        return psycopg2.connect(self.database_url, connect_timeout=10)

    def _ensure_table_exists(self) -> None:
        """Ensure the user_submissions table exists."""
        if self._table_initialized:
            return

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS user_submissions (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            user_name VARCHAR(255) NOT NULL,
                            submission_tag VARCHAR(255) NOT NULL,
                            final_score DECIMAL(6,3) NOT NULL,
                            leaderboard_rank INTEGER,
                            test_1_score DECIMAL(6,3),
                            test_2_score DECIMAL(6,3),
                            test_3_score DECIMAL(6,3),
                            test_4_score DECIMAL(6,3),
                            test_5_score DECIMAL(6,3),
                            test_6_score DECIMAL(6,3),
                            test_7_score DECIMAL(6,3),
                            test_8_score DECIMAL(6,3),
                            test_9_score DECIMAL(6,3),
                            test_10_score DECIMAL(6,3),
                            test_11_score DECIMAL(6,3),
                            test_12_score DECIMAL(6,3),
                            test_13_score DECIMAL(6,3),
                            test_14_score DECIMAL(6,3),
                            test_15_score DECIMAL(6,3),
                            test_16_score DECIMAL(6,3),
                            test_17_score DECIMAL(6,3),
                            test_18_score DECIMAL(6,3),
                            test_19_score DECIMAL(6,3),
                            test_20_score DECIMAL(6,3),
                            UNIQUE(user_name, submission_tag)
                        )
                        """
                    )
                    conn.commit()
                    self._table_initialized = True
        except Exception:
            pass

    def record_submission(
        self,
        user_name: str,
        submission_tag: str,
        final_score: float,
        test_scores: Dict[str, float],
        leaderboard_rank: Optional[int] = None,
    ) -> bool:
        """
        Record a user submission with individual test scores.

        Args:
            user_name: Name of the user/participant
            submission_tag: Tag for this submission
            final_score: Final weighted score
            test_scores: Dictionary of individual test scores (test_1, test_2, etc.)
            leaderboard_rank: Current rank on leaderboard
            
        Returns:
            bool: True if submission was recorded successfully, False otherwise
        """
        try:
            self._ensure_table_exists()

            timestamp = datetime.now()

            score_columns = {
                f"test_{i}_score": test_scores.get(f"test_{i}", None) 
                for i in range(1, 21)
            }

            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    columns = [
                        "user_name",
                        "submission_tag",
                        "timestamp",
                        "final_score",
                        "leaderboard_rank",
                    ] + list(score_columns.keys())

                    values = [
                        user_name,
                        submission_tag,
                        timestamp,
                        final_score,
                        leaderboard_rank,
                    ] + list(score_columns.values())

                    placeholders = ", ".join(["%s"] * len(values))
                    column_names = ", ".join(columns)

                    update_clause = ", ".join(
                        [
                            f"{col} = EXCLUDED.{col}"
                            for col in columns
                            if col not in ["user_name", "submission_tag"]
                        ]
                    )

                    cur.execute(
                        f"""
                        INSERT INTO user_submissions ({column_names})
                        VALUES ({placeholders})
                        ON CONFLICT (user_name, submission_tag)
                        DO UPDATE SET {update_clause}
                        """,
                        values,
                    )
                    conn.commit()
                    return True
        except Exception as e:
            # Log the error but don't crash the submission process
            print(f"Warning: Failed to record submission to database: {e}")
            return False
