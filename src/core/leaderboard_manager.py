"""
Leaderboard Management Module
============================

Manages the hackathon leaderboard using user_submissions table.
"""

import os
import logging
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class LeaderboardManager:
    """Manages leaderboard operations using user_submissions table."""

    def __init__(self):
        """Initialize leaderboard manager."""
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.database_url)

    def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get current leaderboard sorted by score using user_submissions table.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of leaderboard entries with rankings calculated from scores
        """
        logger.debug("Retrieving leaderboard with limit %d", limit)

        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        user_name as participant_name,
                        submission_tag,
                        timestamp,
                        final_score as score,
                        DENSE_RANK() OVER (ORDER BY final_score DESC) as rank
                    FROM user_submissions
                    ORDER BY final_score DESC
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
        Get the rank of a specific participant's latest submission.

        Args:
            participant_name: Name of the participant

        Returns:
            Rank of the participant's latest submission (1-indexed), or 0 if not found
        """
        logger.debug("Looking up rank for participant %s", participant_name)
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    WITH ranked_submissions AS (
                        SELECT
                            user_name,
                            submission_tag,
                            final_score,
                            timestamp,
                            DENSE_RANK() OVER (ORDER BY final_score DESC) as rank
                        FROM user_submissions
                    ),
                    latest_submission AS (
                        SELECT
                            user_name,
                            submission_tag,
                            final_score,
                            timestamp,
                            ROW_NUMBER() OVER (
                                PARTITION BY user_name
                                ORDER BY timestamp DESC
                            ) as rn
                        FROM user_submissions
                        WHERE user_name = %s
                    )
                    SELECT r.rank
                    FROM ranked_submissions r
                    JOIN latest_submission l ON (
                        r.user_name = l.user_name AND
                        r.submission_tag = l.submission_tag
                    )
                    WHERE l.rn = 1
                    """,
                    (participant_name,),
                )
                result = cur.fetchone()
                return int(result[0]) if result else 0