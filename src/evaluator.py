"""
Evaluation Engine Module
========================

Handles evaluation of participant submissions.
"""

import json
from typing import Dict, Any, List, Optional
import random
import hashlib


class EvaluationEngine:
    """Engine for evaluating participant submissions."""

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize evaluation engine.
        
        Args:
            config: EvaluationConfig object with criteria weights
        """
        if config and hasattr(config, 'criteria_weights'):
            self.evaluation_criteria = config.criteria_weights
            self.scoring_config = config.scoring
        else:
            # Default configuration
            self.evaluation_criteria = {
                "accuracy": 0.4,
                "performance": 0.3,
                "completeness": 0.3,
            }
            self.scoring_config = {
                "base_score_range": {"min": 0.6, "max": 0.95},
                "completeness_bonus_max": 0.1,
                "performance_time_threshold": 10.0,
                "performance_memory_threshold": 1000.0
            }

    def evaluate_submission(
        self,
        participant_name: str,
        submission_tag: str,
        results: Dict[str, Any],
        test_data_id: str,
    ) -> Dict[str, Any]:
        """
        Evaluate a participant's submission results.

        Args:
            participant_name: Name of the participant
            submission_tag: Tag for this submission
            results: Results submitted by participant
            test_data_id: ID of the test data used

        Returns:
            Evaluation result with score and details
        """
        try:
            # Validate submission format
            validation_result = self._validate_submission_format(results=results)
            if not validation_result["valid"]:
                return {
                    "valid": False,
                    "error": validation_result["error"],
                    "score": 0.0,
                }

            # Calculate scores for different criteria
            accuracy_score = self._calculate_accuracy_score(results=results)
            performance_score = self._calculate_performance_score(results=results)
            completeness_score = self._calculate_completeness_score(results=results)

            # Calculate weighted final score
            final_score = (
                accuracy_score * self.evaluation_criteria["accuracy"]
                + performance_score * self.evaluation_criteria["performance"]
                + completeness_score * self.evaluation_criteria["completeness"]
            )

            return {
                "valid": True,
                "score": round(final_score, 3),
                "details": {
                    "accuracy_score": round(accuracy_score, 3),
                    "performance_score": round(performance_score, 3),
                    "completeness_score": round(completeness_score, 3),
                    "weighted_scores": {
                        "accuracy": round(
                            accuracy_score * self.evaluation_criteria["accuracy"], 3
                        ),
                        "performance": round(
                            performance_score * self.evaluation_criteria["performance"],
                            3,
                        ),
                        "completeness": round(
                            completeness_score
                            * self.evaluation_criteria["completeness"],
                            3,
                        ),
                    },
                    "criteria_weights": self.evaluation_criteria,
                },
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Evaluation error: {str(e)}",
                "score": 0.0,
            }

    def _validate_submission_format(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the format of submission results.

        Args:
            results: Results to validate

        Returns:
            Validation result
        """
        required_fields = ["processed_data", "metadata"]

        for field in required_fields:
            if field not in results:
                return {"valid": False, "error": f"Missing required field: {field}"}

        # Validate processed_data structure
        if not isinstance(results["processed_data"], dict):
            return {"valid": False, "error": "processed_data must be a dictionary"}

        # Validate metadata structure
        metadata = results.get("metadata", {})
        if not isinstance(metadata, dict):
            return {"valid": False, "error": "metadata must be a dictionary"}

        return {"valid": True}

    def _calculate_accuracy_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate accuracy score based on results.

        Args:
            results: Submission results

        Returns:
            Accuracy score (0.0 to 1.0)
        """
        processed_data = results.get("processed_data", {})

        # Simple mock evaluation - in real implementation,
        # compare against ground truth
        if not processed_data:
            return 0.0

        # Mock: Score based on number of processed items
        num_items = len(processed_data)
        if num_items == 0:
            return 0.0

        # Mock: Random score with some deterministic component
        # In real implementation, this would compare actual vs expected results
        score_seed = str(sorted(processed_data.keys()))
        random.seed(hashlib.md5(score_seed.encode()).hexdigest())
        base_range = self.scoring_config["base_score_range"]
        base_score = random.uniform(base_range["min"], base_range["max"])

        # Bonus for more complete processing
        completeness_bonus = min(
            num_items / 100.0, 
            self.scoring_config["completeness_bonus_max"]
        )

        return min(base_score + completeness_bonus, 1.0)

    def _calculate_performance_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate performance score based on efficiency metrics.

        Args:
            results: Submission results

        Returns:
            Performance score (0.0 to 1.0)
        """
        metadata = results.get("metadata", {})

        # Check for performance metrics
        processing_time = metadata.get("processing_time_seconds")
        memory_usage = metadata.get("memory_usage_mb")

        if processing_time is None:
            # No performance data provided
            return 0.5

        # Mock performance scoring using config thresholds
        # In real implementation, this would have actual benchmarks
        time_threshold = self.scoring_config["performance_time_threshold"]
        time_score = max(0.0, min(1.0, (time_threshold - processing_time) / time_threshold))

        if memory_usage is not None:
            memory_threshold = self.scoring_config["performance_memory_threshold"]
            memory_score = max(0.0, min(1.0, (memory_threshold - memory_usage) / memory_threshold))
            return (time_score + memory_score) / 2.0

        return time_score

    def _calculate_completeness_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate completeness score based on result coverage.

        Args:
            results: Submission results

        Returns:
            Completeness score (0.0 to 1.0)
        """
        processed_data = results.get("processed_data", {})
        metadata = results.get("metadata", {})

        # Score based on completeness indicators
        score = 0.0

        # Check if data was processed
        if processed_data:
            score += 0.5

        # Check if metadata is provided
        if metadata:
            score += 0.2

        # Check for additional quality indicators
        if metadata.get("quality_checks_passed"):
            score += 0.2

        if metadata.get("validation_status") == "passed":
            score += 0.1

        return min(score, 1.0)
