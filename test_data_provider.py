"""
Test Data Provider Module
=========================

Provides test data to participants for evaluation.
"""

import json
import random
import hashlib
from typing import Dict, Any, List
from datetime import datetime


class TestDataProvider:
    """Provides test data for participants to process."""

    def __init__(self):
        """Initialize test data provider."""
        self.data_templates = self._initialize_data_templates()

    def _initialize_data_templates(self) -> Dict[str, Any]:
        """Initialize different types of test data templates."""
        return {
            "simple_math": {
                "description": "Basic mathematical operations",
                "sample_data": [
                    {"operation": "add", "numbers": [5, 3]},
                    {"operation": "multiply", "numbers": [4, 7]},
                    {"operation": "subtract", "numbers": [10, 4]},
                ],
            },
            "text_processing": {
                "description": "Text analysis and processing",
                "sample_data": [
                    {"text": "Hello world", "task": "count_words"},
                    {"text": "Python programming", "task": "reverse"},
                    {"text": "Machine Learning", "task": "uppercase"},
                ],
            },
            "data_analysis": {
                "description": "Data analysis and statistics",
                "sample_data": [
                    {"dataset": [1, 2, 3, 4, 5], "task": "calculate_mean"},
                    {"dataset": [10, 20, 15, 25, 30], "task": "find_max"},
                    {"dataset": [2, 4, 6, 8, 10], "task": "sum_all"},
                ],
            },
        }

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
        # Create deterministic but unique test data based on participant
        seed_string = f"{participant_name}_{submission_tag}"
        random.seed(hashlib.md5(seed_string.encode()).hexdigest())

        # Generate test data ID
        test_data_id = hashlib.sha256(
            f"{participant_name}_{submission_tag}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        # Select and customize test cases
        test_cases = self._generate_test_cases(participant_name=participant_name)

        return {
            "test_data_id": test_data_id,
            "participant_name": participant_name,
            "submission_tag": submission_tag,
            "timestamp": datetime.utcnow().isoformat(),
            "instructions": {
                "description": "Process the provided test cases and return results",
                "expected_format": {
                    "processed_data": "Dictionary with results for each test case",
                    "metadata": {
                        "processing_time_seconds": "Time taken to process",
                        "memory_usage_mb": "Memory usage (optional)",
                        "quality_checks_passed": "Boolean indicating quality",
                        "validation_status": "Status of validation (passed/failed)",
                    },
                },
                "submission_endpoint": "/api/submit-results",
            },
            "test_cases": test_cases,
            "evaluation_criteria": {
                "accuracy": "Correctness of results (40%)",
                "performance": "Processing efficiency (30%)",
                "completeness": "Coverage and metadata (30%)",
            },
        }

    def _generate_test_cases(self, participant_name: str) -> List[Dict[str, Any]]:
        """
        Generate specific test cases for a participant.

        Args:
            participant_name: Name of the participant

        Returns:
            List of test cases
        """
        test_cases = []

        # Add different types of test cases
        for template_name, template_data in self.data_templates.items():
            # Customize based on participant (for deterministic variation)
            participant_hash = hashlib.md5(participant_name.encode()).hexdigest()
            seed_value = int(participant_hash[:8], 16) % 1000

            for i, sample in enumerate(template_data["sample_data"]):
                test_case = {
                    "test_id": f"{template_name}_{i+1}",
                    "type": template_name,
                    "description": template_data["description"],
                    "input_data": self._customize_test_case(
                        sample=sample, seed=seed_value + i
                    ),
                    "expected_output_format": self._get_expected_format(
                        test_type=template_name
                    ),
                }
                test_cases.append(test_case)

        return test_cases

    def _customize_test_case(self, sample: Dict[str, Any], seed: int) -> Dict[str, Any]:
        """
        Customize a test case with deterministic randomization.

        Args:
            sample: Base sample data
            seed: Seed for randomization

        Returns:
            Customized test case
        """
        random.seed(seed)
        customized = sample.copy()

        # Customize based on test type
        if "numbers" in customized:
            # Randomize numbers slightly
            customized["numbers"] = [
                num + random.randint(-2, 2) for num in customized["numbers"]
            ]
        elif "dataset" in customized:
            # Add some variation to dataset
            base_dataset = customized["dataset"]
            customized["dataset"] = [
                val + random.randint(-5, 5) for val in base_dataset
            ]
        elif "text" in customized:
            # Add variations to text processing tasks
            texts = [
                "Hello world",
                "Python programming",
                "Machine Learning",
                "Data Science",
                "Artificial Intelligence",
                "Deep Learning",
            ]
            customized["text"] = random.choice(texts)

        return customized

    def _get_expected_format(self, test_type: str) -> Dict[str, Any]:
        """
        Get expected output format for a test type.

        Args:
            test_type: Type of test case

        Returns:
            Expected output format description
        """
        formats = {
            "simple_math": {
                "result": "Numeric result of the operation",
                "operation_performed": "Description of operation",
            },
            "text_processing": {
                "result": "Processed text result",
                "original_text": "Original input text",
                "task_completed": "Boolean indicating completion",
            },
            "data_analysis": {
                "result": "Calculated statistical result",
                "dataset_size": "Number of data points processed",
                "calculation_method": "Method used for calculation",
            },
        }

        return formats.get(test_type, {"result": "Processed result"})
