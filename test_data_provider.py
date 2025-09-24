"""
Test Data Provider Module
=========================

Provides vehicle configuration test data to participants for evaluation.
"""

import random
import hashlib
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
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
        self.test_case_generators = self._initialize_test_generators()

    def _load_vehicle_data(self) -> pd.DataFrame:
        """Load vehicle configuration data."""
        data_path = Path(__file__).parent / "data" / "jlr_vehicle_configurations.csv"

        if data_path.exists():
            return pd.read_csv(data_path)
        else:
            return pd.DataFrame()

    def _initialize_test_generators(self) -> List[Dict[str, Any]]:
        """Initialize test case generator configurations."""
        return [
            {
                "name": "identical_configs",
                "description": "Two identical vehicle configurations",
                "generator": self._generate_identical_test,
            },
            {
                "name": "single_feature_diff",
                "description": "Configurations differing by one feature",
                "generator": self._generate_feature_diff_test,
            },
            {
                "name": "high_vs_low_spec",
                "description": "High vs low specification comparison",
                "generator": self._generate_spec_comparison_test,
            },
            {
                "name": "price_similarity",
                "description": "Similar price vs distant price comparison",
                "generator": self._generate_price_test,
            },
            {
                "name": "same_vehicle_diff_trim",
                "description": "Same vehicle line with different trim levels",
                "generator": self._generate_trim_test,
            },
        ]

    def generate_test_data(
        self, participant_name: str, submission_tag: str
    ) -> Dict[str, Any]:
        """
        Generate test data for a specific participant.

        Args:
            participant_name: Name of the participant
            submission_tag: Tag for this submission

        Returns:
            Test data package for the participant
        """
        random.seed(self.seed)

        test_data_id = hashlib.sha256(
            f"{participant_name}_{submission_tag}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        test_cases = self._generate_test_cases()

        return {
            "test_data_id": test_data_id,
            "participant_name": participant_name,
            "submission_tag": submission_tag,
            "timestamp": datetime.utcnow().isoformat(),
            "instructions": {
                "description": "Generate embeddings for vehicle configurations",
                "expected_format": {
                    "processed_data": {
                        "test_id": {
                            "embeddings": "List of embedding vectors",
                            "num_configs": "Number of configurations processed",
                        }
                    },
                    "metadata": {
                        "processing_time_seconds": "Time taken to process",
                        "memory_usage_mb": "Memory usage",
                        "quality_checks_passed": "Boolean",
                        "validation_status": "passed/failed",
                        "total_embeddings_generated": "Total count",
                    },
                },
                "submission_endpoint": "/api/submit-results",
            },
            "test_cases": test_cases,
            "evaluation_criteria": {
                "accuracy": "Embedding quality (40%)",
                "performance": "Processing efficiency (30%)",
                "completeness": "Coverage and metadata (30%)",
            },
        }

    def _generate_test_cases(self) -> List[Dict[str, Any]]:
        """Generate test cases using fixed seed for consistency."""
        if self.vehicle_data.empty:
            return []

        random.seed(self.seed)

        test_cases = []

        for i, generator_config in enumerate(self.test_case_generators):
            for j in range(2):
                test_case = generator_config["generator"](seed=self.seed + i * 10 + j)
                if test_case:
                    test_case["test_id"] = f"{generator_config['name']}_{i+1}"
                    test_case["type"] = generator_config["name"]
                    test_case["description"] = generator_config["description"]
                    test_cases.append(test_case)

        return test_cases

    def _generate_identical_test(self, seed: int) -> Dict[str, Any]:
        """Generate test with identical configurations."""
        random.seed(seed)
        vehicle_config = self.vehicle_data.sample(n=1).iloc[0].to_dict()

        return {
            "input_data": {
                "vehicle_configs": [vehicle_config, vehicle_config.copy()],
                "expected_relationship": "identical",
            }
        }

    def _generate_feature_diff_test(self, seed: int) -> Dict[str, Any]:
        """Generate test with single feature difference."""
        random.seed(seed)
        vehicle_config = self.vehicle_data.sample(n=1).iloc[0].to_dict()

        modified_config = vehicle_config.copy()
        features = self._parse_features(vehicle_config.get("Feature_Codes", "[]"))

        if features and len(features) > 1:
            modified_config["Feature_Codes"] = str(features[:-1])

        return {
            "input_data": {
                "vehicle_configs": [vehicle_config, modified_config],
                "expected_relationship": "similar",
            }
        }

    def _generate_spec_comparison_test(self, seed: int) -> Dict[str, Any]:
        """Generate high vs low spec test."""
        random.seed(seed)

        high_trims = ["SV", "SVR", "Autobiography"]
        low_trims = ["S", "SE"]

        high_spec = self.vehicle_data[
            self.vehicle_data["Trim"].isin(high_trims)
        ].sample(n=1)
        low_spec = self.vehicle_data[self.vehicle_data["Trim"].isin(low_trims)].sample(
            n=1
        )

        if high_spec.empty:
            high_spec = self.vehicle_data.nlargest(1, "Total_Price_GBP")
        if low_spec.empty:
            low_spec = self.vehicle_data.nsmallest(1, "Total_Price_GBP")

        return {
            "input_data": {
                "vehicle_configs": [
                    high_spec.iloc[0].to_dict(),
                    low_spec.iloc[0].to_dict(),
                ],
                "expected_relationship": "different",
            }
        }

    def _generate_price_test(self, seed: int) -> Dict[str, Any]:
        """Generate price similarity test."""
        random.seed(seed)
        base_config = self.vehicle_data.sample(n=1).iloc[0].to_dict()
        base_price = base_config["Total_Price_GBP"]

        price_range = base_price * 0.2
        similar_configs = self.vehicle_data[
            (self.vehicle_data["Total_Price_GBP"] >= base_price - price_range)
            & (self.vehicle_data["Total_Price_GBP"] <= base_price + price_range)
        ]

        distant_configs = self.vehicle_data[
            (self.vehicle_data["Total_Price_GBP"] < base_price * 0.5)
            | (self.vehicle_data["Total_Price_GBP"] > base_price * 2.0)
        ]

        similar_config = (
            similar_configs.sample(n=1).iloc[0].to_dict()
            if not similar_configs.empty
            else base_config
        )
        distant_config = (
            distant_configs.sample(n=1).iloc[0].to_dict()
            if not distant_configs.empty
            else base_config
        )

        return {
            "input_data": {
                "vehicle_configs": [base_config, similar_config, distant_config],
                "expected_relationship": "price_correlation",
            }
        }

    def _generate_trim_test(self, seed: int) -> Dict[str, Any]:
        """Generate same vehicle line, different trim test."""
        random.seed(seed)
        vehicle_line = self.vehicle_data["Vehicle_Line"].sample(n=1).iloc[0]
        line_configs = self.vehicle_data[
            self.vehicle_data["Vehicle_Line"] == vehicle_line
        ]

        if len(line_configs) >= 3:
            selected = line_configs.sample(n=3).to_dict(orient="records")
        else:
            selected = self.vehicle_data.sample(n=3).to_dict(orient="records")

        return {
            "input_data": {
                "vehicle_configs": selected,
                "expected_relationship": "same_line_different_trim",
            }
        }

    def _parse_features(self, feature_str: str) -> List[str]:
        """Parse feature string into list."""
        if pd.isna(feature_str) or feature_str == "[]":
            return []
        try:
            return [f.strip().strip("'\"") for f in feature_str.strip("[]").split(",")]
        except Exception:
            return []
