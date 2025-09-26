"""
Test Data Provider Module
=========================

Provides intelligently designed vehicle configuration test data for embedding evaluation.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


class TestDataProvider:
    """Provides vehicle configuration test data designed to evaluate embedding quality."""

    def __init__(self, seed: int, dataset_path: str):
        """Initialize test data provider.

        Args:
            seed: Fixed seed for reproducible test case selection
            dataset_path: Path to vehicle configurations CSV
        """
        self.seed = seed
        self.dataset_path = dataset_path
        self.vehicle_data = self._load_vehicle_data()

    def _load_vehicle_data(self) -> pd.DataFrame:
        """Load and prepare vehicle configuration data."""
        data_path = Path(self.dataset_path)

        if not data_path.exists():
            raise FileNotFoundError(f"Dataset not found at {data_path}")

        df = pd.read_csv(data_path)
        df["Feature_Codes"] = df["Feature_Codes"].apply(ast.literal_eval)
        df["Feature_Count"] = df["Feature_Codes"].apply(len)

        return df

    def generate_test_data(
        self, participant_name: str, submission_tag: str
    ) -> Dict[str, Any]:
        """Generate comprehensive test data for embedding evaluation.

        All participants receive identical test data (parameters unused but kept for API compatibility).

        Args:
            participant_name: Participant identifier (unused)
            submission_tag: Submission version (unused)

        Returns:
            Dictionary mapping test IDs to test configurations
        """
        logger.info("Generating test data for participant %s (%s)", participant_name, submission_tag)
        
        test_data = {
            "test_1": self._test_price_extremes(),
            "test_2": self._test_single_option_difference(),
            "test_3": self._test_model_year_sensitivity(),
            "test_4": self._test_color_sensitivity(),
            "test_5": self._test_trim_level_similarity(),
            "test_6": self._test_vehicle_line_separation(),
            "test_7": self._test_derivative_clustering(),
            "test_8": self._test_feature_count_correlation(),
            "test_9": self._test_transitivity(),
            "test_10": self._test_cross_year_comparison(),
        }
        
        total_configs = sum(len(test_configs) for test_configs in test_data.values())
        logger.info("Generated %d tests with %d total configurations", len(test_data), total_configs)
        
        return test_data

    def _test_price_extremes(self) -> List[Dict[str, Any]]:
        """Test 1: Most expensive vs least expensive configurations should be dissimilar."""
        most_expensive = self.vehicle_data.nlargest(1, "Total_Price_GBP").iloc[0]
        least_expensive = self.vehicle_data.nsmallest(1, "Total_Price_GBP").iloc[0]

        return [
            most_expensive.to_dict(),
            least_expensive.to_dict(),
        ]

    def _test_single_option_difference(self) -> List[Dict[str, Any]]:
        """Test 2: Configs differing by exactly 1 option should be highly similar."""
        df = self.vehicle_data

        config_a = df.iloc[100]
        features_a = set(config_a["Feature_Codes"])

        similar_config = None
        dissimilar_config = None

        for idx in range(101, min(500, len(df))):
            config = df.iloc[idx]
            features = set(config["Feature_Codes"])
            diff = len(features_a.symmetric_difference(features))

            if diff == 1 and similar_config is None:
                similar_config = config
            elif diff > 5 and dissimilar_config is None:
                dissimilar_config = config

            if similar_config is not None and dissimilar_config is not None:
                break

        if similar_config is None:
            similar_config = df.iloc[101]
        if dissimilar_config is None:
            dissimilar_config = df.iloc[200]

        return [
            config_a.to_dict(),
            similar_config.to_dict(),
            dissimilar_config.to_dict(),
        ]

    def _test_model_year_sensitivity(self) -> List[Dict[str, Any]]:
        """Test 3: Model year difference should have moderate impact on similarity."""
        df = self.vehicle_data

        base_config = df[
            (df["Vehicle_Line"] == "Range Rover Sport") & (df["Model_Year"] == 2023)
        ].iloc[0]

        different_year = df[
            (df["Vehicle_Line"] == "Range Rover Sport")
            & (df["Model_Year"] == 2020)
            & (df["Derivative"] == base_config["Derivative"])
        ]

        if len(different_year) > 0:
            year_diff_config = different_year.iloc[0]
        else:
            year_diff_config = df[
                (df["Vehicle_Line"] == "Range Rover Sport") & (df["Model_Year"] == 2020)
            ].iloc[0]

        return [
            base_config.to_dict(),
            year_diff_config.to_dict(),
        ]

    def _test_color_sensitivity(self) -> List[Dict[str, Any]]:
        """Test 4: Color difference alone should have minimal impact (less than option diff)."""
        df = self.vehicle_data

        base_config = df.iloc[300]

        same_except_color = df[
            (df["Vehicle_Line"] == base_config["Vehicle_Line"])
            & (df["Derivative"] == base_config["Derivative"])
            & (df["Trim"] == base_config["Trim"])
            & (df["Model_Year"] == base_config["Model_Year"])
            & (df["Exterior_Colour"] != base_config["Exterior_Colour"])
        ]

        if len(same_except_color) > 0:
            color_diff = same_except_color.iloc[0]
        else:
            color_diff = df.iloc[301]

        return [
            base_config.to_dict(),
            color_diff.to_dict(),
        ]

    def _test_trim_level_similarity(self) -> List[Dict[str, Any]]:
        """Test 5: Same vehicle/year but different trims should show moderate similarity."""
        df = self.vehicle_data

        vehicle_line = "Range Rover"
        year = 2024

        configs = df[(df["Vehicle_Line"] == vehicle_line) & (df["Model_Year"] == year)]

        if len(configs) >= 3:
            selected = configs.iloc[:3]
        else:
            selected = df[df["Vehicle_Line"] == vehicle_line].iloc[:3]

        return [config.to_dict() for _, config in selected.iterrows()]

    def _test_vehicle_line_separation(self) -> List[Dict[str, Any]]:
        """Test 6: Different vehicle lines should be clearly separated in embedding space."""
        df = self.vehicle_data

        vehicle_lines = ["Range Rover Sport", "Discovery Sport", "Defender", "F-Pace"]
        configs = []

        for vl in vehicle_lines:
            vl_configs = df[df["Vehicle_Line"] == vl]
            if len(vl_configs) > 0:
                configs.append(vl_configs.iloc[0].to_dict())

        return configs

    def _test_derivative_clustering(self) -> List[Dict[str, Any]]:
        """Test 7: Configs with same derivative should cluster together."""
        df = self.vehicle_data

        derivative = "P400"
        same_derivative = df[df["Derivative"] == derivative].head(3)

        different_derivative = df[df["Derivative"] == "D250"].head(1)

        configs = list(same_derivative.to_dict(orient="records"))
        if len(different_derivative) > 0:
            configs.append(different_derivative.iloc[0].to_dict())

        return configs

    def _test_feature_count_correlation(self) -> List[Dict[str, Any]]:
        """Test 8: Feature count should correlate with similarity patterns."""
        df = self.vehicle_data

        low_features = df[df["Feature_Count"] <= 6].iloc[0]
        mid_features = df[
            (df["Feature_Count"] >= 9) & (df["Feature_Count"] <= 11)
        ].iloc[0]
        high_features = df[df["Feature_Count"] >= 15].iloc[0]

        return [
            low_features.to_dict(),
            mid_features.to_dict(),
            high_features.to_dict(),
        ]

    def _test_transitivity(self) -> List[Dict[str, Any]]:
        """Test 9: If A similar to B and B similar to C, then A should be somewhat similar to C."""
        df = self.vehicle_data

        vehicle_line = "Range Rover Sport"
        derivative = "P530"

        configs = df[
            (df["Vehicle_Line"] == vehicle_line) & (df["Derivative"] == derivative)
        ].head(3)

        if len(configs) < 3:
            configs = df[df["Vehicle_Line"] == vehicle_line].head(3)

        return [config.to_dict() for _, config in configs.iterrows()]

    def _test_cross_year_comparison(self) -> List[Dict[str, Any]]:
        """Test 10: Same configuration pattern across different years."""
        df = self.vehicle_data

        vehicle_line = "Discovery"
        derivative = "P300"

        year_2023 = df[
            (df["Vehicle_Line"] == vehicle_line)
            & (df["Derivative"] == derivative)
            & (df["Model_Year"] == 2023)
        ]
        year_2025 = df[
            (df["Vehicle_Line"] == vehicle_line)
            & (df["Derivative"] == derivative)
            & (df["Model_Year"] == 2025)
        ]

        configs = []
        if len(year_2023) > 0:
            configs.append(year_2023.iloc[0].to_dict())
        if len(year_2025) > 0:
            configs.append(year_2025.iloc[0].to_dict())

        if len(configs) < 2:
            configs = (
                df[df["Vehicle_Line"] == vehicle_line].head(2).to_dict(orient="records")
            )

        return configs
