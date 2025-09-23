"""
Leaderboard Management Module
============================

Manages the hackathon leaderboard stored in CSV format.
"""

import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class LeaderboardManager:
    """Manages leaderboard operations for the hackathon."""

    def __init__(self, csv_path: str):
        """
        Initialize leaderboard manager.

        Args:
            csv_path: Path to the leaderboard CSV file
        """
        self.csv_path = Path(csv_path)
        self._ensure_csv_exists()

    def _ensure_csv_exists(self) -> None:
        """Ensure the CSV file exists with proper headers."""
        if not self.csv_path.exists():
            # Create directory if it doesn't exist
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)

            # Create CSV with headers
            with open(self.csv_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    ["participant_name", "submission_tag", "timestamp", "score"]
                )

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
        timestamp = datetime.utcnow().isoformat()

        # Read existing data
        existing_data = []
        if self.csv_path.exists():
            with open(self.csv_path, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                existing_data = list(reader)

        # Check if participant already exists
        participant_exists = False
        for i, row in enumerate(existing_data):
            if row["participant_name"] == participant_name:
                # Update if score is better
                if float(row["score"]) < score:
                    existing_data[i] = {
                        "participant_name": participant_name,
                        "submission_tag": submission_tag,
                        "timestamp": timestamp,
                        "score": str(score),
                    }
                participant_exists = True
                break

        # Add new participant if doesn't exist
        if not participant_exists:
            existing_data.append(
                {
                    "participant_name": participant_name,
                    "submission_tag": submission_tag,
                    "timestamp": timestamp,
                    "score": str(score),
                }
            )

        # Sort by score (descending) and write back
        existing_data.sort(key=lambda x: float(x["score"]), reverse=True)

        with open(self.csv_path, "w", newline="") as csvfile:
            fieldnames = ["participant_name", "submission_tag", "timestamp", "score"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_data)

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """
        Get current leaderboard sorted by score.

        Returns:
            List of leaderboard entries with rank information
        """
        if not self.csv_path.exists():
            return []

        leaderboard = []
        with open(self.csv_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for rank, row in enumerate(reader, 1):
                leaderboard.append(
                    {
                        "rank": rank,
                        "participant_name": row["participant_name"],
                        "submission_tag": row["submission_tag"],
                        "timestamp": row["timestamp"],
                        "score": float(row["score"]),
                        "formatted_score": f"{float(row['score']):.3f}",
                    }
                )

        return leaderboard

    def get_participant_rank(self, participant_name: str) -> Optional[int]:
        """
        Get current rank of a specific participant.

        Args:
            participant_name: Name of the participant

        Returns:
            Current rank (1-indexed) or None if not found
        """
        leaderboard = self.get_leaderboard()
        for entry in leaderboard:
            if entry["participant_name"] == participant_name:
                return entry["rank"]
        return None

    def get_top_n(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N participants from leaderboard.

        Args:
            n: Number of top participants to return

        Returns:
            List of top N participants
        """
        leaderboard = self.get_leaderboard()
        return leaderboard[:n]

    def get_participant_history(self, participant_name: str) -> List[Dict[str, Any]]:
        """
        Get submission history for a specific participant.
        Note: Current implementation only keeps best score.

        Args:
            participant_name: Name of the participant

        Returns:
            List of submissions (currently just latest)
        """
        leaderboard = self.get_leaderboard()
        return [
            entry
            for entry in leaderboard
            if entry["participant_name"] == participant_name
        ]
