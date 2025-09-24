"""
Test Data Provider Module
=========================

Provides vehicle configuration test data to participants for evaluation.
"""

import random
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path


class TestDataProvider:
    """Provides vehicle configuration test data for participants to process."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize test data provider.

        Args:
            seed: Fixed seed for random generation to ensure consistency
        """
        self.seed = seed if seed is not None else 42
        self.vehicle_data = self._load_vehicle_data()

    def _load_vehicle_data(self) -> pd.DataFrame:
        """Load vehicle configuration data."""
        data_path = Path(__file__).parent / "data" / "jlr_vehicle_configurations.csv"

        if data_path.exists():
            return pd.read_csv(data_path)
        else:
            return pd.DataFrame()

    def generate_test_data(
        self, participant_name: str, submission_tag: str
    ) -> Dict[str, Any]:
        """
        Generate test data for participants.

        Args:
            participant_name: Name (unused, for API compatibility)
            submission_tag: Tag (unused, for API compatibility)

        Returns:
            Dictionary mapping test IDs to vehicle configurations
        """
        random.seed(self.seed)

        if self.vehicle_data.empty:
            return {}

        test_data = {}

        test_data["test_1"] = self._sample_configs(2)
        test_data["test_2"] = self._sample_configs(2)
        test_data["test_3"] = self._sample_configs(3)
        test_data["test_4"] = self._sample_configs(4)
        test_data["test_5"] = self._sample_configs(2)
        test_data["test_6"] = self._sample_configs(3)
        test_data["test_7"] = self._sample_configs(5)
        test_data["test_8"] = self._sample_configs(2)
        test_data["test_9"] = self._sample_configs(4)
        test_data["test_10"] = self._sample_configs(3)

        return test_data

    def _sample_configs(self, n: int) -> list:
        """Sample n vehicle configurations and return as list of dicts."""
        if len(self.vehicle_data) < n:
            n = len(self.vehicle_data)

        return self.vehicle_data.sample(n=n).to_dict(orient="records")